"""html app views"""

from flask import Blueprint, render_template

app_blueprint = Blueprint("app", __name__)


@app_blueprint.route("/")
def home():
    """home page"""
    return render_template("index.html")
