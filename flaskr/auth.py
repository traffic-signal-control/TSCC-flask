import functools
import sys

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flask_wtf import Form
from wtforms import StringField,SubmitField,PasswordField
from wtforms import validators

bp = Blueprint('auth', __name__, url_prefix='/auth')


class EmailForm(Form):
    email = StringField("Email",[validators.DataRequired("Please enter your email address."),
                                 validators.Email("Please enter your email address.")])
    submit1 = SubmitField('Send Email')


class RegisterForm(Form):
    name = StringField('Username',[validators.DataRequired("Please enter your user name")])
    password = PasswordField('Password')
    email = StringField("Email",[validators.DataRequired("Please enter your email address."),
                                 validators.Email("Please enter your email address.")])
    validate_code = StringField('Validate_code', [validators.DataRequired("Please enter your validation code")])
    submit2 = SubmitField('Submit')


@bp.route('/register_new', methods=('GET', 'POST'))
def register_new():
    form1 = EmailForm()
    form2 = RegisterForm()

    if request.method == 'POST':

        if form1.submit1.data and form1.validate_on_submit():
            print(form1.email.data, file=sys.stderr)
        if form2.submit2.data and form2.validate_on_submit():
            print(form2.name.data, file=sys.stderr)
            print(form2.password.data, file=sys.stderr)
            print(form2.email.data, file=sys.stderr)
            print(form2.validate_code.data, file=sys.stderr)


        #return render_template('auth/register_new.html', form1=form1, form2=form2)

    return render_template('auth/register_new.html', form1=form1, form2=form2)



@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view