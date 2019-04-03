from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr import config
import sys
from copy import deepcopy
import pandas as pd

bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

scenario_dict = deepcopy(config.scenario_dict)
dataset_dict = deepcopy(config.dataset_dict)
user_result_dict = deepcopy(config.user_result)


@bp.route('/')
@login_required
def all():
    """Show all the posts, most recent first."""
    db = get_db()
    submissions = db.execute(
        'SELECT DISTINCT sb.user_id, u.username'
        ' FROM submission sb'
        ' JOIN user u ON sb.user_id = u.id'
    ).fetchall()

    submission_result = []
    for index, submission in enumerate(submissions):
        user_id = submission['user_id']
        username = submission['username']
        user_result_one = get_user_result(user_id)
        user_result_one['username'] = username
        submission_result.append(user_result_one)

    submission_result = pd.DataFrame(submission_result)
    submission_result.sort_values(by='final_result', ascending=False, inplace=True)
    submission_result = submission_result.to_dict('records')

    info = get_user_result(g.user['id'])
    return render_template('leaderboard/index.html',
                           submissions=enumerate(submission_result),
                           returned_info=info,
                           dataset_dict=enumerate(list(dataset_dict.keys())))


def get_user_result(user_id):
    """Get the user result by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    user_result = deepcopy(user_result_dict)
    user_result['user_id'] = user_id

    db = get_db()
    for scen_index, scen_name in dataset_dict.items():
        submission = db.execute(
            'SELECT sb.id, dataset, result, dataset, created'
            ' FROM submission sb'
            ' WHERE sb.user_id = ? AND dataset = ?'
            ' ORDER BY result DESC',
            (user_id,scen_name)
        ).fetchone()

        if submission is None:
            user_result['dataset_result'][scen_index] = 0
        else:
            user_result['dataset_result'][scen_index] = submission['result']

    user_result['final_result'] = get_final_score(user_result['dataset_result'])

    return user_result


def get_final_score(results):
    result = 0
    for k, r in results.items():
        if r is None:
            result += 0
        else:
            result += r
    if len(results) > 0:
        return result/len(results)
    else:
        return 0




