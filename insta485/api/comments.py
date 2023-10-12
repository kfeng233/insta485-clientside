"""REST API for comments."""
import flask
import insta485
from insta485.api.posts import authenticate


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comments():
    """Post comment."""
    connection = insta485.model.get_db()
    # Session cookies authentication
    if 'username' in flask.session:
        username = flask.session['username']
    # HTTP Basic Access Authentication: no credentials or invalid credentials
    elif flask.request.authorization and authenticate(connection):
        username = flask.request.authorization['username']
    else:
        response = {
            "message": "Forbidden",
            "status_code": 403
        }
        return flask.jsonify(response), 403

    postid = flask.request.args.get("postid", default=-1, type=int)
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ?",
        [postid]
    )
    content = cur.fetchall()
    if not content:
        response = {
            "message": "Not Found",
            "status_code": 404
        }
        return flask.jsonify(response), 404
    text = flask.request.json['text']
    connection.execute(
        """INSERT INTO comments (owner, postid, text)
        VALUES (?, ?, ?)""",
        [username, postid, text]
    )
    cur = connection.execute(
        "SELECT last_insert_rowid() AS commentid "
        "FROM comments "
    )
    content = cur.fetchall()
    context = content[0]
    context["lognameOwnsThis"] = True
    context["owner"] = username
    context["ownerShowUrl"] = f"/users/{username}/"
    context["text"] = text
    context["url"] = f"/api/v1/comments/{context['commentid']}/"

    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete comment."""
    connection = insta485.model.get_db()
    # Session cookies authentication
    if 'username' in flask.session:
        username = flask.session['username']
    # HTTP Basic Access Authentication: no credentials or invalid credentials
    elif flask.request.authorization and authenticate(connection):
        username = flask.request.authorization['username']
    else:
        response = {
            "message": "Forbidden",
            "status_code": 403
        }
        return flask.jsonify(response), 403
    cur = connection.execute(
        "SELECT * "
        "FROM comments "
        "WHERE commentid = ?",
        (commentid,)
    )
    comments_content = cur.fetchall()
    if not comments_content:
        response = {
            "message": "Not Found",
            "status_code": 404
        }
        return flask.jsonify(response), 404
    if comments_content[0]['owner'] != username:
        response = {
            "message": "Forbidden",
            "status_code": 403
        }
        return flask.jsonify(response), 403
    connection.execute(
        "DELETE FROM comments WHERE owner = ? AND commentid = ?",
        [username, commentid]
    )
    return flask.jsonify(**{}), 204
