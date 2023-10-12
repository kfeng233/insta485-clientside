"""REST API for likes."""
import flask
import insta485
from functools import wraps
from insta485.api.posts import authenticate
'''
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
'''


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    """Post like."""
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
    cur = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE postid = ? AND owner = ? ",
        [postid, username]
    )
    content = cur.fetchall()
    flag = False
    if not content:
        flag = True
        connection.execute(
            "INSERT INTO likes (owner, postid)"
            "VALUES (?,?)",
            [username, postid]
        )
        cur = connection.execute(
            "SELECT last_insert_rowid() AS likeid "
            "FROM likes "
        )
        content = cur.fetchall()
    context = content[0]
    context["url"] = "/api/v1/likes/"+str(context["likeid"])+"/"
    return flask.jsonify(**context), 201 if flag else 200


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete like."""
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
        "FROM likes "
        "WHERE likeid = ?",
        (likeid,)
    )
    likes_content = cur.fetchall()
    if not likes_content:
        response = {
            "message": "Not Found",
            "status_code": 404
        }
        return flask.jsonify(response), 404
    elif likes_content[0]['owner'] != username:
        response = {
            "message": "Forbidden",
            "status_code": 403
        }
        return flask.jsonify(response), 403
    else:
        cur = connection.execute(
            "DELETE FROM likes WHERE owner = ? AND likeid = ?",
            [username, likeid]
        )
        return flask.jsonify(**{}), 204
