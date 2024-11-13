from flask import Blueprint

direccion_bp = Blueprint('direccion', __name__, template_folder='templates')

from . import routes