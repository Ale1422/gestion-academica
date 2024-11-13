from flask import Blueprint

secretaria_bp = Blueprint('secretaria', __name__, template_folder='templates')

from . import routes