from flask import  render_template,jsonify
# from flask_login import current_user
# from app.models import Post
from . import direccion_bp


@direccion_bp.route("/direccion")
def index():
    try:
        return render_template("direccion/index.html")
    except Exception as e:
            return jsonify(error=str(e)), 500