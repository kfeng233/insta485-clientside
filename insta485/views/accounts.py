"""
Insta485 accounts view.

URLs include:
/accounts/login/ screenshot (no user logged in)
/accounts/logout/ Immediate redirect. No screenshot.
/accounts/create/ screenshot (no user logged in)
/accounts/delete/ screenshot
/accounts/edit/ screenshot
/accounts/password/
/accounts/auth/
"""
import os
import hashlib
import pathlib
import uuid
import flask
import insta485


def verify(mpassword, connection, username):
    """Verify."""
    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        [username]
    )
    content = cur.fetchall()
    if not content:
        return False
    password_db_string = content[0]['password']
    algorithm, salt, password_hash = password_db_string.split('$')
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + mpassword
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash_new = hash_obj.hexdigest()

    return password_hash == password_hash_new


@insta485.app.route('/accounts/login/')
def login():
    """Login."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/create/')
def create():
    """Create."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    return flask.render_template("create.html")


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout."""
    # print("DEBUG Logout:", flask.session['username'])
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/delete/')
def delete():
    """Delete."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    context = {"username": flask.session['username']}
    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/')
def edit():
    """Edit."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    print("DEBUG", flask.session['username'])
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT fullname, email "
        "FROM users "
        "WHERE username = ?",
        [flask.session['username']]
    )
    content = cur.fetchall()
    context = content[0]
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/')
def password():
    """Password."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    return flask.render_template("password.html")


# AWS only
@insta485.app.route('/accounts/auth/')
def auth():
    """Auth."""
    if 'username' in flask.session:
        # Not quite sure if it's right here
        return ''
    flask.abort(403)


def cal_pass_entry(real_password):
    """Calculate password entry."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + real_password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    return password_db_string


def save_upload(fileobj):
    """
    Compute base name (filename without directory).

    We use a UUID to avoid
    clashes with existing files, and ensure that
    the name is compatible with the
    filesystem. For best practive, we ensure uniform file extensions
    (e.g.lowercase).
    """
    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    return uuid_basename


def helper_func_login(connection):
    """Help to login."""
    username = flask.request.form['username']
    mpassword = flask.request.form['password']
    if len(username) == 0 or len(mpassword) == 0:
        flask.abort(400)
    if not verify(mpassword, connection, username):
        flask.abort(403)
    flask.session['username'] = username


def helper_func_create(connection):
    """Help to create."""
    username = flask.request.form['username']
    mpassword = flask.request.form['password']
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    fileobj = flask.request.files["file"]

    if not username or not mpassword or not fullname \
            or not email or not fileobj:
        flask.abort(400)

    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        [username,]
    )
    content = cur.fetchall()
    if content:
        flask.abort(409)

    # Save upload
    uuid_basename = save_upload(fileobj)

    # Calculate password entry
    password_db_string = cal_pass_entry(mpassword)

    # Write to database
    cur = connection.execute(
        "INSERT INTO users \
        (username, fullname, email, filename, password) \
        VALUES (?,?,?,?,?)",
        [username, fullname, email, uuid_basename, password_db_string]
    )
    flask.session['username'] = username


def helper_func_delete(connection):
    """Help to delete."""
    if 'username' not in flask.session:
        flask.abort(403)
    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        [flask.session['username']]
    )
    content = cur.fetchall()
    file_path = content[0]['filename']
    path = insta485.app.config["UPLOAD_FOLDER"]/file_path

    # Delete upload icon
    try:
        os.remove(path)
    except OSError:
        # print(f"Error when delete file: {err}", 500)
        flask.abort(500)

    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        [flask.session['username']]
    )
    content = cur.fetchall()

    for file in content:
        file_path = file['filename']
        path = insta485.app.config["UPLOAD_FOLDER"]/file_path

        # Delete upload icon
        try:
            os.remove(path)
        except OSError:
            # print(f"Error when delete file: {err}", 500)
            flask.abort(500)
    cur = connection.execute(
        "DELETE FROM users WHERE username = ?",
        [flask.session['username']]
    )
    flask.session.clear()


def helper_func_edit_account(connection):
    """Help to edit account."""
    if 'username' not in flask.session:
        flask.abort(403)
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    fileobj = flask.request.files["file"]

    if not fullname or not email:
        flask.abort(400)
    if fileobj:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            [flask.session['username']]
        )
        content = cur.fetchall()
        file_path = content[0]['filename']
        path = insta485.app.config["UPLOAD_FOLDER"]/file_path

        # Delete upload icon
        try:
            os.remove(path)
        except OSError:
            # return f"Error when delete file: {err}", 500
            flask.abort(500)

        # Save upload
        uuid_basename = save_upload(fileobj)

        cur = connection.execute(
            "UPDATE users \
            SET fullname=?, email=?, filename=?\
            WHERE username=?",
            [fullname, email, uuid_basename, flask.session['username']]
        )
    else:
        cur = connection.execute(
            "UPDATE users \
            SET fullname=?, email=?\
            WHERE username=?",
            [fullname, email, flask.session['username']]
        )


def helper_func_update_password(connection):
    """Help to update password."""
    if 'username' not in flask.session:
        flask.abort(403)
    mpassword = flask.request.form['password']
    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']

    if not mpassword or not new_password1 or not new_password2:
        flask.abort(400)
    if not verify(mpassword, connection, flask.session['username']):
        flask.abort(403)
    if new_password1 != new_password2:
        flask.abort(401)

    # Calculate password entry
    password_db_string = cal_pass_entry(new_password1)
    connection.execute(
        "UPDATE users \
        SET password=? \
        WHERE username=?",
        [password_db_string, flask.session['username']]
    )
    # print("Reache pass",url,len(url))


@insta485.app.route('/accounts/', methods=['POST'])
def accounts():
    """Accounts."""
    # flask.session['username'] = "Yuning"
    url = flask.request.args.get('target', '')
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()

    if operation == 'login':
        helper_func_login(connection)
    elif operation == 'create':
        helper_func_create(connection)
    elif operation == 'delete':
        helper_func_delete(connection)
    elif operation == 'edit_account':
        helper_func_edit_account(connection)
    elif operation == 'update_password':
        helper_func_update_password(connection)

    if len(url) != 0:
        return flask.redirect(url)
    return flask.redirect(flask.url_for("show_index"))
