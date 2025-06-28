from flask import Flask
from config import Config, basedir
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

# Initialize the Flask application
app = Flask(__name__)

# Load configuration from Config object
app.config.from_object(Config)

# Initialize extensions
db: SQLAlchemy = SQLAlchemy(app)          # Database ORM
migrate = Migrate(app, db)                # Database migrations
login_manager = LoginManager(app)         # User session management
Session(app)                              # Server-side sessions
mail = Mail(app)                          # Email support

# Configure login manager
login_manager.login_view = 'auth.login'   # Redirect to login page if not logged in
login_manager.login_message = 'Login Required'  # Message for login required

# Import routes and models to register them with the app
from app import routes
from app.auth import routes
from app.articles import routes
from app.profile import routes
from app.auth.models import *
from app.articles.models import *

# Import blueprints
from app import auth, articles, profile

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(articles.bp)
app.register_blueprint(profile.bp)

# Register custom Jinja filter
from app.utils.func import utc_to_local
app.jinja_env.filters['utc_to_local'] = utc_to_local
