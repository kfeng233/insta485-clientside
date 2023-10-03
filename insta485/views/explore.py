"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
import insta485


@insta485.app.route('/explore/')
def explore():
    """Get the unfollowing users."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        """
        SELECT users.filename, users.username
        FROM users
        WHERE users.username != ? AND users.username NOT IN (
        SELECT username2 FROM following WHERE username1 = ?)""",
        (flask.session['username'], flask.session['username'], )
    )
    unfollowers = cur.fetchall()
    print(unfollowers)
    context = {"unfollowers": unfollowers}
    return flask.render_template("explore.html", **context)
