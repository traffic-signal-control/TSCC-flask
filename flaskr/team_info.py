from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug import secure_filename

from wtforms import StringField, SubmitField, PasswordField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import Form
from flaskr.auth import login_required, activate_required
from flaskr.db import get_db
from flaskr import config
import sys
import os
import time
import pandas as pd

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

        # maintain the submission result
    g.submission_result = submission_result

    info = get_info()
    return render_template('team_info/index.html', submissions=enumerate(submission_result_list), returned_info=info)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def check_upload_file(planFile, num_step):
    flag = True
    error_info = ''
    try:
        plan = pd.read_csv(planFile, sep='\t', header=0, dtype=int)
    except:
        flag = False
        error_info = 'The format of signal plan is not valid and cannot be read by pd.read_csv!'
        print(error_info)
        return flag

    intersection_id = plan.columns[0]
    if intersection_id != 'intersection_1_1':
        flag = False
        error_info = 'The header intersection_id is wrong (for example: intersection_1_1)!'
        print(error_info)
        return flag

    phases = plan.values
    current_phase = phases[0][0]

    if len(phases) < num_step:
        flag = False
        error_info = 'The time of signal plan is less than the default time!'
        print(error_info)
        return flag

    if current_phase == 0:
        yellow_time = 1
    else:
        yellow_time = 0

    # get first green phase and check
    last_green_phase = '*'
    for num_phase in range(1, len(phases)):

        next_phase = phases[num_phase][0]

        # check phase itself
        if next_phase not in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
            flag = False
            error_info = 'Phase must be in [0, 1, 2, 3, 4, 5, 6, 7, 8]!'
            break
        if next_phase == '':
            continue

        # check changing phase
        if next_phase != current_phase and next_phase != 0 and current_phase != 0:
            flag = False
            error_info = '5 seconds of yellow time must be inserted between two different phase!'
            break

        # check unchangeable phase
        if next_phase != 0 and next_phase == last_green_phase:
            flag = False
            error_info = 'No yellow light is allowed between the same phase!'
            break

        # check yellow time
        if next_phase != 0 and yellow_time != 0 and yellow_time != 5:
            flag = False
            error_info = 'Yellow time must be 5 seconds!'
            break

        # normal
        if next_phase == 0:
            yellow_time += 1
            if current_phase != 0:
                last_green_phase = current_phase
        else:
            yellow_time = 0
        current_phase = next_phase

    error_info = "In line %s: "%str(num_phase+1) + error_info
    if not flag:
        print(error_info)
    return flag, error_info

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

            num_step = 3600

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
                # limit submission time
                db = get_db()
                submissions = db.execute(
                    'SELECT result, created'
                    ' FROM submission sb'
                    ' JOIN user u'
                    ' ON sb.user_id = u.id AND sb.user_id = ? AND created > datetime("now","-1 day")'
                    ' ORDER BY created DESC',
                    (g.user['id'],)
                ).fetchall()
                submission_result = pd.DataFrame(submissions)
                submission_result.columns = ['result', 'submission_time']
                # if len(submission_result[submission_result['result'].notnull()]) > 10:
                if len(submission_result) >= 10:
                    error = "Submission over 10 times during past 24 hours"
                else:
                    filename = "signal_plan-"+str(g.user['id']) + "-%s"%_time  + "-%s.txt"%dataset_name
                    if not os.path.exists(UPLOAD_FOLDER):
                        os.makedirs(UPLOAD_FOLDER)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))

                    flag, error_info = check_upload_file(os.path.join(UPLOAD_FOLDER, filename), num_step)
                    if not flag:
                        error = 'File uploaded is invalid.\n' + error_info
            else:
                error = 'Signal plan is required and the file name must have a ".txt" extension'

            if error is not None:
                flash(error)
            else:
                db.execute(
                    'INSERT INTO submission (user_id, dataset, file_name)'
                    ' VALUES (?, ?, ?)',
                    (g.user['id'], dataset_name, filename)
                )
                db.commit()
                return redirect(url_for('team_info.all'))
        else:
            print(form.submit.data,file=sys.stderr)
            print(form.validate_on_submit(),file=sys.stderr)
            print(form.errors,file=sys.stderr)
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




