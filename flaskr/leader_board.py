# from flask import (
#     Blueprint, flash, g, redirect, render_template, request, url_for
# )
# from werkzeug.exceptions import abort
#
# from flaskr.auth import login_required
# from flaskr.db import get_db
# from flaskr import config
# import sys
#
# bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')
#
# scenario_dict = config.scenario_dict
# dataset_dict = config.dataset_dict
#
#
# @bp.route('/')
# @login_required
# def all():
#     """Show all the posts, most recent first."""
#     db = get_db()
#     submissions = db.execute(
#         'SELECT sb.user_id, result, dataset, created'
#         ' FROM submission sb'
#         ' JOIN user u ON sb.user_id = u.id AND  sb.user_id = ?'
#         ' ORDER BY created DESC',
#         (g.user['id'],)
#     ).fetchall()
#     print(scenario_dict, file=sys.stderr)
#     submission_result_list = []
#     for index, submission in enumerate(submissions):
#         submission_result = dict()
#         submission_result['index'] = index + 1
#         submission_result['scenario'] = scenario_dict[submission['dataset']]
#         if submission['result'] is None:
#             submission_result['result'] = "Calculating.."
#         else:
#             submission_result['result'] = str(submission['result'])
#
#         submission_result['user_id'] = submission['user_id']
#         submission_result['created'] = submission['created']
#
#         submission_result_list.append(submission_result)
#
#     info = get_rank()
#     return render_template('team_info/index.html', submissions=enumerate(submission_result_list), returned_info=info)
#
# @bp.route('/get_rank', methods=('GET', 'POST'))
# @login_required
# def get_rank():
#     """Get the user info by id.
#
#     Checks that the id exists and optionally that the current user is
#     the author.
#
#     :param id: id of post to get
#     :param check_author: require the current user to be the author
#     :return: the post with author information
#     :raise 404: if a post with the given id doesn't exist
#     :raise 403: if the current user isn't the author
#     """
#     db = get_db()
#     for scen_index, scen_name in dataset_dict:
#
#         submission = db.execute(
#             'SELECT sb.user_id, result, dataset, created'
#             ' FROM submission sb'
#             ' JOIN user u ON sb.user_id = u.id AND  sb.user_id = ?'
#             ' ORDER BY created DESC',
#             (g.user['id'],)
#         ).fetchall()
#
#     post = get_db().execute(
#         'SELECT username, password'
#         ' FROM user u WHERE u.id = ?',
#         (g.user['id'],)
#     ).fetchone()
#
#     if post is None:
#         abort(404, "User id {0} doesn't exist.".format(id))
#
#     return post
#
#
#
#
