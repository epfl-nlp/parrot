import os
import traceback

from flask import jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from openai import OpenAIError, APITimeoutError, RateLimitError
from jsonschema import ValidationError
from werkzeug.exceptions import HTTPException

from app import app
from api import APIException
from database import db
from account import account_api
from user import user_api
from chat import chat_api

VERSION = "1.0.0"

CORS(app)
migrate = Migrate()


@app.errorhandler(APIException)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(APITimeoutError)
def handle_openai_error_timeout(e):
    app.logger.error(traceback.format_exc())
    return jsonify({"error": "OpenAI timed out."}), 504


@app.errorhandler(RateLimitError)
def handle_openai_error_ratelimit(e):
    app.logger.error(traceback.format_exc())
    return jsonify({"error": "OpenAI rate limit hit."}), 429


@app.errorhandler(OpenAIError)
def handle_openai_error(e):
    app.logger.error(traceback.format_exc())
    return jsonify({"error": str(e)}), 500


@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return jsonify({"error": original_error.message}), 400
    return jsonify({"error": "Bad Request"}), 400


@app.errorhandler(HTTPException)
def handle_not_found(e):
    app.logger.error(traceback.format_exc())
    return jsonify({"error": str(e)}), e.code


@app.errorhandler(Exception)
def handle_server_error(e):
    app.logger.error(traceback.format_exc())
    return jsonify({"error": "Server Error"}), 500


@app.route("/")
def heartbeat():
    return "Running"


def init_app():
    print(f"Running version {VERSION}")
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(account_api)
    app.register_blueprint(user_api)
    app.register_blueprint(chat_api)
    return app


def main():
    port = int(os.environ.get("FLASK_RUN_PORT", 8080))
    app = init_app()
    app.run(debug=os.environ.get("FLASK_DEBUG", False), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
