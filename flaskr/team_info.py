from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('team_info', __name__, url_prefix='/team_info')


@bp.route('/')
def all():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        'SELECT sb.id, result, body, created, author_id, username'
        ' FROM submission sb JOIN user u ON sb.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    info = get_info()
    return render_template('team_info/index.html', submissions=posts, returned_info=info)


@bp.route('/submit', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new submission for the current user."""
    print("====================YES")
    if request.method == 'POST':
        result = request.form['title']
        body = request.form['body']
        error = None

        if not body:
            error = 'Submission is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO submission (result, body, author_id)'
                ' VALUES (?,?, ?)',
                (result, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('team_info.all'))

    return render_template('team_info/submit.html')


@bp.route('/get_info', methods=('GET', 'POST'))
@login_required
def get_info():
    """Get the user info by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = get_db().execute(
        'SELECT username, password'
        ' FROM user u WHERE u.id = ?',
        (g.user['id'],)
    ).fetchone()

    if post is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    return post




