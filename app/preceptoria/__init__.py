from flask import Blueprint

preceptoria_bp = Blueprint('preceptoria_bp', __name__, template_folder='templates')

from . import routes