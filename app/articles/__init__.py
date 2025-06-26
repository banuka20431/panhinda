from flask.blueprints import Blueprint
from flask import Blueprint

bp = Blueprint('articles', __name__, url_prefix='/articles')
