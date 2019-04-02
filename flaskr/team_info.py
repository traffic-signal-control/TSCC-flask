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
    return render_template('team_info/index.html', posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    submission = get_db().execute(
        'SELECT sb.id, result, body, created, author_id, username'
        ' FROM submission sb JOIN user u ON sb.author_id = u.id'
        ' WHERE sb.id = ?',
        (id,)
    ).fetchone()

    if submission is None:
        abort(404, "Submission id {0} doesn't exist.".format(id))

    if check_author and submission['author_id'] != g.user['id']:
        abort(403)

    return submission


@bp.route('/submit', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
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
            return redirect(url_for('index'))

    return redirect(url_for('index'))



