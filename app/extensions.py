from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager  # type: ignore
from flask_mail import Mail
from app.logging_config import init_logging
import logging

# Initialize logger
init_logging()
logger = logging.getLogger("panhinda_logger")

# Database ORM
db = SQLAlchemy()

# User session management
login_manager = LoginManager()

# Email support
mail = Mail()
