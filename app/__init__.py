from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load default config
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    # Load instance config if present
    app.config.from_pyfile("config.py", silent=True)

    @app.route("/")
    def index():
        return "Flask app is running."

    return app
