from flask import abort, render_template
# from flask_login import current_user
# from app.models import Post
from . import public_bp


@public_bp.route("/")
def index():
    return render_template("public/index.html")
