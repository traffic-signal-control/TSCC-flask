from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort

from wtforms import StringField, SubmitField, PasswordField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import Form
from flaskr.auth import login_required, activate_required
from flaskr.db import get_db
from flaskr import config
import sys
import os
import time

bp = Blueprint('team_info', __name__, url_prefix='/team_info')

UPLOAD_FOLDER = os.path.join("evaluate", "submitted")
ALLOWED_EXTENSIONS = set(['txt'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

scenario_dict = config.scenario_dict
dataset_dict = config.dataset_dict

@bp.route('/')
@login_required
def all():
    """Show all the posts, most recent first."""
    db = get_db()
    submissions = db.execute(
        'SELECT sb.user_id, result, dataset, created'
        ' FROM submission sb'
        ' JOIN user u ON sb.user_id = u.id AND  sb.user_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    print(scenario_dict, file=sys.stderr)
    submission_result_list = []
    for index, submission in enumerate(submissions):
        submission_result = dict()
        submission_result['index'] = index + 1
        submission_result['scenario'] = scenario_dict[submission['dataset']]
        if submission['result'] is None:
            submission_result['result'] = "Calculating.."
        else:
            submission_result['result'] = str(submission['result'])

        submission_result['user_id'] = submission['user_id']
        submission_result['created'] = submission['created']

        submission_result_list.append(submission_result)

    info = get_info()
    return render_template('team_info/index.html', submissions=enumerate(submission_result_list), returned_info=info)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


class UploadForm(Form):
    dataset = SelectField(label='Dataset', choices = [('default', '--'),
                                                      ('scenario_1', 'scenario_1'),
                                                      ('scenario_2', 'scenario_2'),
                                                      ('scenario_3', 'scenario_3'),
                                                      ('scenario_4', 'scenario_4'),
                                                      ('scenario_5', 'scenario_5'),
                                                      ])
    file = FileField(validators=[FileAllowed(ALLOWED_EXTENSIONS, u'Only .txt file is supported!'), FileRequired(u'Please select a ".txt" file.')])
    submit = SubmitField(u'Submit')

@bp.route('/submit', methods=('GET', 'POST'))
@activate_required
def create():
    """Create a new submission for the current user."""
    form = UploadForm()
    if request.method == 'POST':
        dataset = form.dataset.data
        file = form.file.data

        if form.validate_on_submit():
            error = None

            print(dataset, file=sys.stderr)
            print(file.filename)
            dataset_name = None
            if dataset == 'default':
                error = 'Please select one dataset'
            elif dataset in dataset_dict:
                dataset_name = dataset_dict[dataset]
            else:
                error = 'Please select one dataset'

            _time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
            filename = None
            if file and allowed_file(file.filename):
                filename = "signal_plan-"+str(g.user['id']) + "-%s"%_time  + "-%s.txt"%dataset_name
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
                    (g.user['id'], dataset_name, filename)
                )
                db.commit()
                return redirect(url_for('team_info.all'))
        else:
            print(form.submit.data,file=sys.stderr)
            print(form.validate_on_submit(),file=sys.stderr)
            print(form.errors,file=sys.stderr)
            flash("form.validate_on_submit()")
            render_template('team_info/submit.html', form=form)

    return render_template('team_info/submit.html', form=form)


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
        'SELECT username, id, email'
        ' FROM user u WHERE u.id = ?',
        (g.user['id'],)
    ).fetchone()

    if post is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    return post




