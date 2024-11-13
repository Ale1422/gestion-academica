from flask import  render_template
# from flask_login import current_user
# from app.models import Post
from . import direccion_bp


@direccion_bp.route("/direccion")
def index():
    return render_template("direccion/index.html")