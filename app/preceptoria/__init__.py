from flask import Blueprint

preceptoria_bp = Blueprint('preceptoria', __name__, template_folder='templates')

from . import routes