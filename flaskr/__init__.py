import os

from flask import Flask, render_template, make_response, jsonify
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

csp = {
    'default-src': ['\'self\'','*.mailsite.com','*.googleapis.com','*.bootcss.com'],
    'img-src': '*',
    'script-src': ['\'self\'', '\'unsafe-inline\'','\'unsafe-eval\'','*.bootcss.com','*.mathjax.org'],
    'style-src': ['\'self\'','\'unsafe-inline\'','*.googleapis.com','*.bootcss.com'],
    'font-src': ['\'self\'','data:','about:', 'fonts.gstatic.com']
}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    csrf = CSRFProtect()

    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    Talisman(app,content_security_policy=csp) #,content_security_policy_nonce_in=['script-src','style-src','img-src','font-src'])
    csrf.init_app(app)


    app.config.update(PERMANENT_SESSION_LIFETIME=600)
    app.config.update(WTF_CSRF_ENABLED=False)

    app.config['MAIL_SERVER'] = 'smtp.live.com'
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'trafficsignalcontrol@hotmail.com'
    app.config['MAIL_PASSWORD'] = 'tsc123456'
    app.config['MAIL_DEBUG'] = True


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
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/home')
    def home():
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

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return make_response(
                jsonify(error="ratelimit exceeded %s" % e.description)
                , 429
        )

    limiter = Limiter(app, default_limits = ["2/hour"], key_func=get_remote_address)

    from . import db 
    db.init_app(app)

    from . import auth
    limiter.limit("40/hour")(auth.bp)
    app.register_blueprint(auth.bp)

    from . import team_info
    limiter.limit("40/hour")(team_info.bp)
    app.register_blueprint(team_info.bp)

    from . import leader_board
    app.register_blueprint(leader_board.bp)

    return app

app = create_app()