from flask import Blueprint

calendario_bp = Blueprint('calendario_bp', __name__, template_folder='templates')

from app.calendario import routes  # noqa: E402,F401 — registra las rutas al importar el blueprint