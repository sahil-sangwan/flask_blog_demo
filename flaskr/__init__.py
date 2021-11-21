import os

from flask import Flask

def create_app(test_config = None):
    # Make the flask instance, initialized with the module name
    # and so that the config file is in the instance directory
    # (not committed to github)
    app = Flask(__name__, instance_relative_config=True)
    # for development, configure the flask instance to have a simple
    # secret key and also define the path to the sqlite file.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    # Check if the app is being used in testing mode
    if test_config is None:
        # Override default config with specs from config.py (in
        # instance directory)
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # Attempt to make the instance directory (which will house the
    # sqlite and config files)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # This block registers the init_db and close_db commands to the app instance.
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp) #bp is a module-level variable for the blueprint

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
    
    return app
