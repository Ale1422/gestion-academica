from flask import Blueprint

materia_bp = Blueprint('materia', __name__, template_folder='templates')

from . import routes