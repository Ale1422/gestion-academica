from flask import abort, render_template
# from flask_login import current_user
# from app.models import Post
from . import preceptoria_bp


@preceptoria_bp.route("/preceptoria")
def index():
    return render_template("preceptoria/index.html")