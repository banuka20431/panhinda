from typing import Any, cast

from flask import Flask
from flask_migrate import Migrate

from config import Config
from flask_session import Session  # type: ignore
from app.extensions import mail, logger, login_manager, db

# Initialize the Flask application
app: Flask = Flask(__name__)

# Load configuration from Config object
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)  # type: ignore
mail.init_app(app)
migrate = Migrate(app, db)
Session(app)  # Server-side sessions

# Configure login manager
login_manager.login_view = cast(Any, "auth.login")
login_manager.login_message = "Login Required"
login_manager.login_message_category = "info"

# Import blueprints
from app import auth, articles, profile

from app import routes  # pyright: ignore[reportUnusedImport]
from app.articles import routes  # pyright: ignore[reportUnusedImport]
from app.auth import routes  # pyright: ignore[reportUnusedImport]
from app.profile import routes  # pyright: ignore[reportUnusedImport]

# Register blueprints
app.register_blueprint(auth.bp)  # type: ignore
app.register_blueprint(articles.bp)  # type: ignore
app.register_blueprint(profile.bp)  # type: ignore

# Register custom Jinja filter
from app.utils.func import utc_to_local

app.jinja_env.filters["utc_to_local"] = utc_to_local  # type: ignore

logger.info("Application initialized successfully")
