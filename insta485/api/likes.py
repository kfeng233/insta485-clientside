"""REST API for likes."""
import flask
import insta485
from insta485.api.posts import all_check, login_check


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    """Post like."""
    connection = insta485.model.get_db()
    response, statuscode, username, postid = all_check(connection)
    if response:
        return flask.jsonify(response), statuscode

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
    response, username = login_check(connection)
    if response:
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
    if likes_content[0]['owner'] != username:
        response = {
            "message": "Forbidden",
            "status_code": 403
        }
        return flask.jsonify(response), 403

    cur = connection.execute(
        "DELETE FROM likes WHERE owner = ? AND likeid = ?",
        [username, likeid]
    )
    return flask.jsonify(**{}), 204
