from flask import Blueprint, jsonify, request
from flask_expects_json import expects_json

from api import get_users, create_user
from auth import auth, ADMIN_ROLE

user_api = Blueprint("user_api", __name__)

user_schema = {
    "required": ["code"],
    "properties": {
        "name": {"type": "string"},
        "code": {"type": "string"},
        "account_id": {"type": "integer"},
    },
}


@user_api.route("/api/users", methods=["GET"])
@auth.login_required(role=ADMIN_ROLE)
def handle_get_users():
    users = get_users()
    return jsonify([user.to_dict() for user in users])


@user_api.route("/api/users", methods=["POST"])
@auth.login_required(role=ADMIN_ROLE)
@expects_json(user_schema)
def handle_add_user():
    name = request.json.get("name")
    code = request.json["code"]
    account_id = request.json.get("account_id")
    user = create_user(name=name, code=code, account_id=account_id)
    return jsonify(user.to_dict()), 201
