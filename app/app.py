"""main app entry point"""

from flask import Flask
from src.base import Database
from views_api import api_blueprint
from views_app import app_blueprint


def setup_database() -> None:
    """setup empty database with tables"""
    db_handler = Database()
    _ = db_handler.validate()
    db_handler.finish()


setup_database()

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(app_blueprint)
app.static_folder = "static"

if __name__ == "__main__":
    app.run()
