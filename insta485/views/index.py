"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
import insta485


@insta485.app.route('/uploads/<path:filename>')
def get_image_url(filename):
    """Get the URL for the image."""
    if 'username' not in flask.session:
        flask.abort(403)
    try:
        img_path = insta485.app.config['UPLOAD_FOLDER']
        return flask.send_from_directory(img_path, filename)
    except FileNotFoundError:
        flask.abort(404)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # User login
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session['username']
    # Connect to database
    connection = insta485.model.get_db()
    users = get_users_data(connection)
    posts = get_posts_data(logname, connection)
    comments = get_comments_data(connection)
    context = {"users": users, "posts": posts, "comments": comments}
    return flask.render_template("index.html", **context)


def get_users_data(connection):
    """Get the users data."""
    cur = connection.execute(
        "SELECT username, fullname, filename "
        "FROM users ")
    users = cur.fetchall()
    return users


def get_posts_data(logname, connection):
    """Get the posts from logname and their following users."""
    cur = connection.execute("""
        SELECT
            users.username,
            posts.postid,
            posts.filename,
            posts.created,
            posts.owner
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE users.username = ? OR users.username IN (
            SELECT username2 FROM following WHERE username1 = ?)
        ORDER BY postid DESC""", (logname, logname))
    posts = cur.fetchall()
    posts = index_posts_helper(posts, connection, logname)
    return posts


def index_posts_helper(posts, connection, logname):
    """Help set post."""
    for post in posts:
        # convert the time since the post was created in human-readable format
        past = arrow.get(post['created'], 'YYYY-MM-DD HH:mm:ss')
        cur_time = arrow.utcnow()
        post['created'] = past.humanize(cur_time)
        # get like status for each post
        cur = connection.execute("""
            SELECT postid, owner
            FROM likes
            WHERE postid = ? AND owner= ?
            """, (post['postid'], logname, ))
        likes_status = cur.fetchall()
        # get number of likes based on post id
        cur = connection.execute("""
            SELECT COUNT(postid)
            FROM likes
            WHERE postid = ?
        """, (post['postid'], ))
        num_likes = cur.fetchall()
        post.update({"num_likes": num_likes[0]['COUNT(postid)'],
                     "likes_status": len(likes_status)})
    return posts


def get_likes_data(logname, postid, connection):
    """Get the likes data and calculate the number of like for each post."""
    cur = connection.execute("""
        SELECT COUNT(*) AS liked
        FROM likes
        WHERE owner = ? AND postid = ?
        """, (logname, postid)
    )
    likes_status = cur.fetchall()
    return likes_status


def get_comments_data(connection):
    """Get comment data by the time in ascending order."""
    cur = connection.execute("""
        SELECT *
        FROM comments
        ORDER BY commentid ASC
        """)
    comments = cur.fetchall()
    return comments
