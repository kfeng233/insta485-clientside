"""
Insta485 comment view.

URLs include:
/comments/?target=URL
"""

import flask
import insta485


@insta485.app.route('/comments/', methods=['POST'])
def comments():
    """Handle comments post request."""
    # flask.session['username'] = "Yuning"
    url = flask.request.args.get('target', '')
    operation = flask.request.form['operation']
    # Connect to database
    connection = insta485.model.get_db()
    if operation == 'create':
        text = flask.request.form['text']
        postid = flask.request.form['postid']
        if len(text) == 0:
            flask.abort(400)
        else:
            connection.execute(
                """INSERT INTO comments (owner, postid, text)
                VALUES (?, ?, ?)""",
                [flask.session['username'], postid, text]
            )
    elif operation == 'delete':
        commentid = flask.request.form['commentid']
        cur = connection.execute(
            "SELECT * "
            "FROM comments "
            "WHERE commentid = ? AND owner = ?",
            [commentid, flask.session['username']]
        )
        content = cur.fetchall()
        if not content:
            flask.abort(403)
        else:
            cur = connection.execute(
                "DELETE FROM comments WHERE commentid = ?",
                (commentid, )
            )
    if len(url):
        return flask.redirect(url)
    return flask.redirect(flask.url_for('show_index'))
