from flask import Flask
from config import Config, basedir
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)

app.config.from_object(Config)

db: SQLAlchemy = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
Session(app)
mail = Mail(app)

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Login Required'



from app import routes
from app.auth import routes
from app.articles import routes
from app.profile import routes
from app.auth.models import *
from app.articles.models import *

from app import auth, articles, profile

app.register_blueprint(auth.bp)
app.register_blueprint(articles.bp)
app.register_blueprint(profile.bp)


from app.utils.func import utc_to_local

app.jinja_env.filters['utc_to_local'] = utc_to_local
