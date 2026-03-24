from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        from app.config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Alembic can detect them
    from app.models import bike  # noqa: F401

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
    from app.routes.commands.bikes import commands_bp
    from app.routes.queries.bikes import queries_bp
    from app.routes.queries.health import health_bp
    app.register_blueprint(commands_bp)
    app.register_blueprint(queries_bp)
    app.register_blueprint(health_bp)

    return app
