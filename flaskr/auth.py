import functools
import sys

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms import validators
from flask_mail import Mail
from flask_mail import Message
from threading import Thread

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 异步发送邮件
def async_send_mail(app, msg, mail):
    # 必须在程序上下文中才能发送邮件，新建的线程没有，因此需要手动创建
    with app.app_context():
        # 发送邮件
        mail.send(msg)


def send_mail(to, subject, **kwargs):
    # 获取原始的app实例
    app = current_app._get_current_object()
    mail = Mail(app)
    # 创建邮件对象
    msg = Message(subject, recipients=[to], sender=app.config['MAIL_USERNAME'])
    msg.body = "dfsadasd"
    msg.html = "<b>testsdsding</b>"
    thr = Thread(target=async_send_mail, args=[app, msg, mail])
    thr.start()
    return thr


class UserForm(FlaskForm):
    email = StringField('Email',[validators.Email("Please enter your email address.")])
    name = StringField('Username',[validators.DataRequired("Please enter your user name")])
    password = PasswordField('Password')

    submit1 = SubmitField('Send Email')


class CodeForm(FlaskForm):

    validate_code = StringField('Code', [validators.DataRequired("Please enter your validation code")])
    submit2 = SubmitField('Register')

class UploadForm(FlaskForm):
    """用户上传文件的表单"""
    '''
    file1 = FileField(
        label="Scenario 1 signal plan:",
        validators=[
            # 文件必须选择;
            FileRequired(),
            # 指定文件上传的格式;
            FileAllowed(['txt'], 'only .txt')
        ]
    )
    '''


@bp.route('/register', methods=('GET', 'POST'))
def register():

    form = UserForm()
    

    if request.method == 'POST':
        db = get_db()
        if form.submit1.data and form.validate_on_submit():
            username = form.name.data
            password = form.password.data
            email = form.email.data
            print(username, file=sys.stderr)
            print(password, file=sys.stderr)
            print(email, file=sys.stderr)
            send_mail(email, "aaaaaaaaaaa")
            db.execute(
                'INSERT INTO user (username, password, email, code) VALUES (?, ?, ?, ?)',
                (username, generate_password_hash(password), email, 'xxx')
            )
            db.commit()
            session['name'] = form.name.data
            flash('注册成功，请移步至邮箱查看验证码激活')
            return redirect(url_for('auth.activate'))
        # if form2.submit2.data and form2.validate_on_submit():

        #     # print(form2.email.data, file=sys.stderr)
        #     print(form2.validate_code.data, file=sys.stderr)


        #return render_template('auth/register_new.html', form1=form1, form2=form2)

    return render_template('auth/register.html', form=form)

@bp.route('/activate', methods=('GET', 'POST'))
def activate():
    form = CodeForm()
    if request.method == 'POST':
        if form.submit2.data and form.validate_on_submit():
            db = get_db()
            username = session['name']
            code = form.validate_code.data
            print(username, file=sys.stderr)
            print(code, file=sys.stderr)
            user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
            error = None
            if error is None:
                return redirect(url_for('auth.login'))

    return render_template('auth/activate.html', form=form)



# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         elif db.execute(
#             'SELECT id FROM user WHERE username = ?', (username,)
#         ).fetchone() is not None:
#             error = 'User {} is already registered.'.format(username)

#         if error is None:
#             db.execute(
#                 'INSERT INTO user (username, password) VALUES (?, ?)',
#                 (username, generate_password_hash(password))
#             )
#             db.commit()
#             return redirect(url_for('auth.login'))

#         flash(error)

#     return render_template('auth/register.html')



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

def activate_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['activate']!=0:
            return redirect(url_for('auth.activate'))

        return view(**kwargs)

    return wrapped_view