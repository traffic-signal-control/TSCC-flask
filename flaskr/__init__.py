import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/home')
    def index():
        return render_template('index.html')

    @app.route('/data_description')
    def data():
        return render_template('data_description.html')

    @app.route('/evaluation')
    def evaluation():
        return render_template('evaluation.html')

    @app.route('/problem_definition')
    def problem_definition():
        return render_template('problem_definition.html')

    @app.route('/rules')
    def rules():
        return render_template('rules.html')

    @app.route('/sample_code')
    def sample_code():
        return render_template('sample_code.html')

    @app.route('/simulator')
    def simulator():
        return render_template('simulator.html')

    @app.route('/submission_guidelines')
    def submission_guidelines():
        return render_template('submission_guidelines.html')

    from . import db 
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import team_info
    app.register_blueprint(team_info.bp)

    return app