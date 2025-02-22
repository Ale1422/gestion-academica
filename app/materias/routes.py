from flask import abort, render_template

from . import materia_bp


@materia_bp.route("/preceptoria")
def index():
    return render_template("preceptoria/index.html")