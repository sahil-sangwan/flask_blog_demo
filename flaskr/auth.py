import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error_msg = None

        if not username:
            error_msg = 'Username is required'
        elif not password:
            error_msg = 'Password is required'

        if error_msg is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error_msg = f'User {username} is already registered'
        else:
            return redirect(url_for('auth.login'))

        flash(error_msg)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error_msg = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error_msg = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error_msg = 'Incorrect password'

        if error_msg is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error_msg)

    return render_template('auth/login.html')

@bp.before_app_request #runs before ANY view function is executed, for ALL endpoints
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else: #the assignment to g.user lasts only as long as the request that needs to use it
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#defining a decorator to confirm that a user is logged in before request
def login_required(view): #wraps the view that it is applied to
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view #returns the newly defined wrapper function


