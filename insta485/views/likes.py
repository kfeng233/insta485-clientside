"""
Insta485 likes view.

URLs include:
/likes/?target=URL
"""

import flask
import insta485


@insta485.app.route('/likes/', methods=['POST'])
def likes():
    """Likes."""
    # flask.session['username'] = "Yuning"
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    url = flask.request.args.get('target', '')
    operation = flask.request.form['operation']
    postid = flask.request.form['postid']
    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * "
        "FROM likes "
        "WHERE postid = ? AND owner = ?",
        (postid, flask.session['username'])
    )
    likes_content = cur.fetchall()
    # user hasn't liked the post
    if operation == 'like':
        if likes_content:
            flask.abort(409)
        else:
            cur = connection.execute(
                "INSERT INTO likes (owner, postid)"
                "VALUES (?,?)",
                [flask.session['username'], postid]
            )
    # user liked the post
    elif operation == 'unlike':
        if not likes_content:
            flask.abort(409)
        else:
            cur = connection.execute(
                "DELETE FROM likes WHERE owner = ? AND postid = ?",
                [flask.session['username'], postid]
            )
    print("url is " + url)
    if len(url):
        return flask.redirect(url)
    return flask.redirect(flask.url_for('show_index'))
