"""
Insta485 users view.

URLs include:
/users/<user_url_slug>/
/users/<user_url_slug>/followers/
/users/<user_url_slug>/following/
"""
import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/")
def show_users(user_url_slug):
    """Show users."""
    # Temp use. Should be deleted later
    # flask.session['username'] = 'awdeorio'

    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    connection = insta485.model.get_db()

    cur = connection.execute(
        'SELECT fullname FROM users WHERE username = ?',
        [user_url_slug]
    )
    content = cur.fetchall()

    if not content:
        flask.abort(404)
    fullname = content[0]['fullname']
    cur = connection.execute(
        'SELECT * FROM following WHERE username1 = ? AND username2 = ?',
        [flask.session['username'], user_url_slug]
    )
    content = cur.fetchall()
    logname_follows_username = bool(content)

    cur = connection.execute(
        'SELECT COUNT(postid) FROM posts WHERE owner = ?',
        [user_url_slug]
    )
    content = cur.fetchall()
    total_posts = content[0]['COUNT(postid)']

    cur = connection.execute(
        'SELECT COUNT(username1) FROM following WHERE username2 = ?',
        [user_url_slug]
    )
    content = cur.fetchall()
    realfollowers = content[0]['COUNT(username1)']

    cur = connection.execute(
        'SELECT COUNT(username2) FROM following WHERE username1 = ?',
        [user_url_slug]
    )
    content = cur.fetchall()
    realfollowing = content[0]['COUNT(username2)']

    cur = connection.execute(
        'SELECT postid, filename FROM posts WHERE owner = ?',
        [user_url_slug]
    )
    posts = cur.fetchall()

    context = {"username": user_url_slug,
               "logname": flask.session['username'],
               "logname_follows_username": logname_follows_username,
               "total_posts": total_posts,
               "followers": realfollowers,
               "following": realfollowing,
               "fullname": fullname,
               "posts": posts,
               "user_url_slug": user_url_slug
               }
    return flask.render_template("users.html", **context)


@insta485.app.route("/users/<user_url_slug>/followers/")
def followers(user_url_slug):
    """Followers."""
    # Temp use. Should be deleted later
    # flask.session['username'] = 'awdeorio'
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT * FROM users WHERE username = ?',
        [user_url_slug]
    )
    content = cur.fetchall()
    if not content:
        flask.abort(404)
    cur = connection.execute("""
        SELECT f.username1 AS username,
        CASE
            WHEN EXISTS ( SELECT 1 from following ff
                             WHERE ff.username1 = ?
                             AND ff.username2 = f.username1 )
                             THEN true
                             ELSE false
        END AS logname_follows_username,
        users.filename
        FROM following f
        JOIN users ON f.username1 = users.username
        WHERE username2 = ? """, (flask.session['username'], user_url_slug))
    content = cur.fetchall()
    # print(content)
    context = {"followers": content, "logname": flask.session['username'],
               'user_url_slug': user_url_slug}
    return flask.render_template("followers.html", **context)


@insta485.app.route("/users/<user_url_slug>/following/")
def following(user_url_slug):
    """Following."""
    # Temp use. Should be deleted later
    # flask.session['username'] = 'awdeorio'
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT * FROM users WHERE username = ?',
        [user_url_slug]
    )
    content = cur.fetchall()
    if not content:
        flask.abort(404)
    cur = connection.execute("""
        SELECT f.username2 AS username,
        CASE
            WHEN EXISTS ( SELECT 1 from following ff WHERE ff.username1 = ?
                             AND ff.username2 = f.username2 )
                             THEN true
                             ELSE false
        END AS logname_follows_username,
        users.filename
        FROM following f
        JOIN users ON f.username2 = users.username
        WHERE username1 = ? """, (flask.session['username'], user_url_slug))
    content = cur.fetchall()
    context = {"following": content, "logname": flask.session['username'],
               'user_url_slug': user_url_slug}
    return flask.render_template("following.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def follow_user():
    """Follow or unfollow user."""
    # flask.session['username'] = "Yuning"
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session['username']  # "awdeorio"
    url = flask.request.args.get('target', '')
    operation = flask.request.form['operation']
    username = flask.request.form['username']
    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )
    follow_content = cur.fetchall()
    # user hasn't liked the post
    if operation == 'follow':
        if follow_content:
            flask.abort(409)
        else:
            cur = connection.execute(
                "INSERT INTO following (username1, username2) VALUES (?,?)",
                [logname, username]
            )
    # user liked the post
    elif operation == 'unfollow':
        if not follow_content:
            flask.abort(409)
        else:
            cur = connection.execute(
                "DELETE FROM following WHERE username1 = ? AND username2 = ?",
                [logname, username]
            )
    if len(url):
        return flask.redirect(url)
    return flask.redirect(flask.url_for('show_index'))
