from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required, activate_required
from flaskr.db import get_db
import sys
import os
import time

bp = Blueprint('team_info', __name__, url_prefix='/team_info')

UPLOAD_FOLDER = os.path.join("flaskr", "uploads", "tmp")
ALLOWED_EXTENSIONS = set(['txt'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

@bp.route('/')
@login_required
def all():
    """Show all the posts, most recent first."""
    db = get_db()
    submission = db.execute(
        'SELECT sb.user_id, result, dataset, created'
        ' FROM submission sb'
        ' JOIN user u ON sb.user_id = u.id AND  sb.user_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    info = get_info()
    return render_template('team_info/index.html', submissions=enumerate(submission), returned_info=info)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@bp.route('/submit', methods=('GET', 'POST'))
@activate_required
def create():
    """Create a new submission for the current user."""
    if request.method == 'POST':
        dataset = request.form['dataset']
        file = request.files['file']
        error = None

        print(dataset, file=sys.stderr)
        print(file.filename)
        if dataset == 'default':
            error = 'Please select one dataset'

        _time = time.strftime('%m_%d_%H_%M_%S', time.localtime(time.time()))
        filename = None
        if file and allowed_file(file.filename):
            filename = str(g.user['id']) + "_" + dataset + "_%s.txt"%_time
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            error = 'Signal plan is required and the file name must have a ".txt" extension'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO submission (user_id, dataset, file_name)'
                ' VALUES (?,?, ?)',
                (g.user['id'], dataset, filename)
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




