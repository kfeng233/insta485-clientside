"""
Insta485 posts view.

URLs include:
/posts/<postid_url_slug>/
"""
import os
import pathlib
import arrow
import click
import flask
import insta485
from insta485.views import index
from insta485.views.accounts import save_upload


@insta485.app.route("/posts/", methods=['POST'])
def handle_post():
    """Handle a post."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    url = flask.request.args.get('target', '')
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    upload_path = insta485.app.config['UPLOAD_FOLDER']
    # delete a post including uploading picture, comments, likes
    if operation == 'delete':
        postid = flask.request.form['postid']
        cur = connection.execute("""
            SELECT * FROM posts WHERE postid = ? AND owner = ?
        """, (postid, flask.session['username']))
        post_data = cur.fetchall()
        # if the owner of the post doesn't match with the logged user
        if not post_data:
            flask.abort(403)
        else:
            connection.execute("""
                DELETE FROM posts WHERE postid = ?
                """, (postid, ))
            # remove the post image physically
            file_path = os.path.join(upload_path, post_data[0]['filename'])
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding="utf-8"):
                    os.remove(file_path)
            else:
                click.echo(f'Unable to delete {file_path}.')
    elif operation == 'create':
        # File handling
        # check if the post request has the file part
        if 'file' not in flask.request.files:
            flask.flash('No file part')
            return flask.redirect(url)
        fileobj = flask.request.files['file']
        suffix = pathlib.Path(fileobj.filename).suffix.lower().strip(".")
        # Unsupported file type.
        if suffix not in insta485.app.config['ALLOWED_EXTENSIONS']:
            flask.flash('Unsupported file type.')
            return flask.redirect(url)
        uuid_basename = save_upload(fileobj)
        cur = connection.execute("""
            INSERT INTO posts (filename, owner)
            VALUES (?, ?) """, (uuid_basename, flask.session['username']))
    if len(url):
        return flask.redirect(url)
    return flask.redirect(flask.url_for(
        'show_users', user_url_slug=flask.session['username']
    ))


@insta485.app.route("/posts/<postid_url_slug>/")
def show_post(postid_url_slug):
    """Display the clicked post."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session['username']
    # Connect to database
    connection = insta485.model.get_db()
    post = get_post_data(logname, postid_url_slug, connection)
    users = index.get_users_data(connection)
    comments = get_comments_data(postid_url_slug, connection)
    context = {"post": post[0], "users": users, "comments": comments}
    return flask.render_template("posts.html", **context)


def get_post_data(logname, postid_url_slug, connection):
    """Get the post data based on post id."""
    cur = connection.execute("""
        SELECT
            posts.postid,
            posts.filename,
            posts.created,
            posts.owner,
            users.username
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE postid = ?""", (postid_url_slug, ))
    post = cur.fetchall()
    past = arrow.get(post[0]['created'], 'YYYY-MM-DD HH:mm:ss')
    cur_time = arrow.utcnow()
    post[0]['created'] = past.humanize(cur_time)
    # get number of likes based on post id
    cur = connection.execute("""
        SELECT COUNT(postid)
        FROM likes
        WHERE postid = ?
    """, (postid_url_slug, )
    )
    num_likes = cur.fetchall()
    # get like status for each post
    cur = connection.execute("""
        SELECT postid, owner
        FROM likes
        WHERE postid = ? AND owner= ?
        """, (postid_url_slug, logname, )
    )
    likes_status = cur.fetchall()
    post[0].update({"num_likes": num_likes[0]['COUNT(postid)'],
                    "likes_status": len(likes_status)})
    return post


def get_comments_data(postid_url_slug, connection):
    """Get comment data by the time in ascending order."""
    cur = connection.execute("""
        SELECT *
        FROM comments
        WHERE postid = ?
        ORDER BY commentid ASC
        """, (postid_url_slug, )
    )
    comments = cur.fetchall()
    return comments
