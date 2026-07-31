from flask import Blueprint

secretaria_bp = Blueprint('secretaria_bp', __name__, template_folder='templates')

from . import routes