"""REST API for posts."""
import hashlib
import flask
import insta485
from insta485.views.accounts import verify
from insta485.views.posts import get_comments_data


@insta485.app.route('/api/v1/posts/')
def get_page():
    """Show posts in pagination."""
    connection = insta485.model.get_db()
    # Session cookies authentication
    if 'username' in flask.session:
        username = flask.session['username']
        response = get_page_helper(connection, username)
        return response
    # HTTP Basic Access Authentication: no credentials or invalid credentials
    if flask.request.authorization and authenticate(connection):
        username = flask.request.authorization['username']
        response = get_page_helper(connection, username)
        return response
    flask.abort(403)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post based on postid."""
    connection = insta485.model.get_db()
    # Session cookies authentication
    if 'username' in flask.session:
        username = flask.session['username']
        cur_post = get_each_post_helper(connection, postid_url_slug, username)
        if not cur_post:
            response = {
                "message": "Not Found",
                "status_code": 404
            }
            return flask.jsonify(response), 404
        return flask.jsonify(cur_post)
    # HTTP Basic Access Authentication: no credentials or invalid credentials
    if flask.request.authorization and authenticate(connection):
        username = flask.request.authorization['username']
        cur_post = get_each_post_helper(connection, postid_url_slug, username)
        if not cur_post:
            response = {
                "message": "Not Found",
                "status_code": 404
            }
            return flask.jsonify(response), 404
        return flask.jsonify(cur_post)
    flask.abort(403)


def authenticate(connection):
    """Handle HTTP Basic Access Authentication."""
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    # HTTP Basic Access Authentication: no credentials or invalid credentials
    return verify(password, connection, username)


def get_page_helper(connection, username):
    """Get the posts based on postid_lte, size and page."""
    # get the parameters
    cur = connection.execute("""
        SELECT MAX(postid) 
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE (users.username = ? OR users.username IN (
            SELECT username2 FROM following WHERE username1 = ?))
        """, (username, username))
    max_postid = cur.fetchone()
    max_postid = max_postid['MAX(postid)']
    postid_lte = flask.request.args.get('postid_lte', default=max_postid, type=int)
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    if postid_lte < 0 or size < 0 or page < 0:
        response = {
            "message": "Bad Request",
            "status_code": 400
        }
        return flask.jsonify(response), 400
    else:
        # get the postid
        cur = connection.execute("""
            SELECT
                posts.postid
            FROM posts
            JOIN users ON posts.owner = users.username
            WHERE (users.username = ? OR users.username IN (
                SELECT username2 FROM following WHERE username1 = ?))
                AND posts.postid <= ?
            ORDER BY postid DESC
            LIMIT ?
            OFFSET ?""", (username, username, postid_lte, size, page*size))
        posts = cur.fetchall()
        for post in posts:
            post.update({"url": "/api/v1/posts/{}/".format(post['postid'])})
        # calculate the next page url
        next_url = ""
        if len(posts) == size:
            next_url = flask.url_for('get_page', size=size, page=page+1, postid_lte=postid_lte)
        cur_path = flask.request.environ['RAW_URI']
        response = {"next": next_url, "results": posts, "url": cur_path}
        return flask.jsonify(**response)


def get_each_post_helper(connection, postid_url_slug, username):
    """Get the info of a post."""
    # get the post comments
    post_comments = get_each_post_comments(postid_url_slug, connection, username)
    comments_url = f'/api/v1/comments/?postid={postid_url_slug}'
    # get the post likes info
    post_likes = get_each_post_likes(connection, username, postid_url_slug)
    # get the post info
    cur = connection.execute("""
        SELECT 
            posts.created AS posts_created, 
            users.filename AS user_filename, 
            owner, 
            posts.filename AS post_filename
        FROM users
        JOIN posts ON users.username = posts.owner
        WHERE users.username = ? AND posts.postid = ?""",
        (username, postid_url_slug))
    content = cur.fetchall()
    # return empty if the post doesn't exist
    if not content:
        return
    # hardcode the context
    ownerImgUrl = content[0]['user_filename']
    imgUrl = content[0]['post_filename']
    cur_path = flask.request.environ['RAW_URI']
    context = {
        "comments": post_comments, 
        "comments_url": comments_url,
        "created": content[0]['posts_created'],
        "imgUrl": '/uploads/{}'.format(imgUrl),
        "likes": post_likes,
        "owner": username,
        "ownerImgUrl": '/uploads/{}'.format(ownerImgUrl),
        "ownerShowUrl": "/users/{}/".format(username),
        "postShowUrl": "/posts/{}/".format(postid_url_slug),
        "postid": postid_url_slug,
        "url": cur_path
    }
    return context


def get_each_post_comments(postid_url_slug, connection, username):
    """Get the post comments."""
    post_comments = get_comments_data(postid_url_slug, connection)
    for post_comment in post_comments:
        if post_comment['owner'] == username:
            post_comment.update({'lognameOwnsThis': True})
        else:
            post_comment.update({'lognameOwnsThis': False})
        post_comment.update({'ownerShowUrl': '/users/{}/'.format(post_comment['owner']),
                             'url': '/api/v1/comments/{}/'.format(post_comment['commentid'])})
        post_comment.pop('created')
        post_comment.pop('postid')
    return post_comments


def get_each_post_likes(connection, username, postid_url_slug):
    """Get like status for each post."""
    cur = connection.execute("""
        SELECT postid, owner, likeid
        FROM likes
        WHERE postid = ? AND owner= ?
        """, (postid_url_slug, username, ))
    likes_status = cur.fetchall()
    if not likes_status:
        url = None
    else:
        url = "/api/v1/likes/{}/".format(likes_status[0]['likeid'])
    # get number of likes based on post id
    cur = connection.execute("""
        SELECT COUNT(postid)
        FROM likes
        WHERE postid = ?
    """, (postid_url_slug, ))
    num_likes = cur.fetchall()
    context = {"numLikes": num_likes[0]['COUNT(postid)'],
            "lognameLikesThis": len(likes_status) == 1,
            "url": url}
    return context
