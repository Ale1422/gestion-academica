# app/__init__.py

from flask import Flask, app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from werkzeug.middleware.proxy_fix import ProxyFix

login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    app.config.from_object(Config)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    db.init_app(app)
    migrate.init_app(app, db)

    from .errors import errors_bp
    app.register_blueprint(errors_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .direccion import direccion_bp
    app.register_blueprint(direccion_bp)

    from .preceptoria import preceptoria_bp
    app.register_blueprint(preceptoria_bp)

    from .secretaria import secretaria_bp
    app.register_blueprint(secretaria_bp)

    from .materias import materia_bp
    app.register_blueprint(materia_bp, url_prefix = '/materias')

    from .calendario import calendario_bp
    app.register_blueprint(calendario_bp)


    return app