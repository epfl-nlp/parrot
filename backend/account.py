from flask import Blueprint, jsonify, request
from flask_expects_json import expects_json

from app import app
from api import get_accounts, create_account, update_account, delete_account, get_num_chats
from auth import auth, ADMIN_ROLE

account_api = Blueprint("account_api", __name__)

account_schema = {
    "required": ["name", "course"],
    "properties": {
        "name": {"type": "string"},
        "course": {"type": "string"},
        "budget": {"type": "integer"},
        "users": {"type": "array", "items": {"type": "integer"}},
    },
}

update_account_schema = {
    "required": [],
    "properties": {
        "name": {"type": "string"},
        "course": {"type": "string"},
        "budget": {"type": "integer"},
        "users": {"type": "array", "items": {"type": "integer"}},
    },
}


@account_api.route("/api/accounts", methods=["GET"])
@auth.login_required(role=ADMIN_ROLE)
def handle_get_accounts():
    active = request.args.get("active", "true").lower() == "true"
    usage = request.args.get("usage", None)
    name = request.args.get("name", None)
    accounts = get_accounts(active=active, usage=usage, name=name)
    return jsonify([account.to_dict() for account in accounts]), 200


@account_api.route("/api/accounts", methods=["POST"])
@auth.login_required(role=ADMIN_ROLE)
@expects_json(account_schema)
def handle_add_account():
    name = request.json["name"]
    course = request.json["course"]
    budget = request.json.get("budget", app.config["DEFAULT_BUDGET"])
    users = request.json.get("users", [])
    account = create_account(name=name, course=course, budget=budget, user_ids=users)
    return jsonify(account.to_dict()), 201


@account_api.route("/api/accounts/<int:account_id>", methods=["PUT"])
@auth.login_required(role=ADMIN_ROLE)
@expects_json(update_account_schema)
def handle_update_account(account_id):
    name = request.json.get("name")
    course = request.json.get("course")
    budget = request.json.get("budget")
    users = request.json.get("users")
    account = update_account(
        account_id=account_id, name=name, course=course, budget=budget, user_ids=users
    )
    return jsonify(account.to_dict()), 200


@account_api.route("/api/accounts/<int:account_id>", methods=["DELETE"])
@auth.login_required(role=ADMIN_ROLE)
def handle_delete_account(account_id):
    account = delete_account(account_id=account_id)
    return jsonify(account.to_dict()), 200


@account_api.route("/api/accounts/<int:account_id>/num_chats", methods=["GET"])
@auth.login_required(role=ADMIN_ROLE)
def handle_get_num_chats(account_id):
    num_chats = get_num_chats(account_id=account_id)
    return jsonify({"num_chats": num_chats}), 200