from flask import render_template
# from flask_login import current_user
# from app.models import Post
from . import secretaria_bp


@secretaria_bp.route("/secretaria")
def index():
    return render_template("secretaria/index.html")