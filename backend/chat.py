from flask import Blueprint, jsonify, request
from flask_expects_json import expects_json

from app import app
from api import get_chats, create_chat, get_messages, ask, check_account_chat, get_num_messages
from auth import auth, USER_ROLE
from utils import clean_string

chat_api = Blueprint("chat_api", __name__)

chat_schema = {
    "required": ["name"],
    "properties": {
        "name": {"type": "string"},
        "model_type": {"type": "string"},
        "instruction_prefix": {"type": "string"},
        "user_prefix": {"type": "string"},
        "assistant_prefix": {"type": "string"},
    },
}

message_schema = {
    "required": ["content"],
    "properties": {
        "content": {"type": "string"},
        "instruction": {"type": "string"},
        "model_args": {
            "type": "object",
            "properties": {
                "temperature": {"type": "number", "default": 0.7},
                "top_p": {"type": "number", "default": 1.0},
                "max_tokens": {"type": "integer", "default": 100},
                "presence_penalty": {"type": "number", "default": 0},
                "frequency_penalty": {"type": "number", "default": 0},
            },
        },
    },
}


@chat_api.route("/api/chats", methods=["GET"])
@auth.login_required(role=USER_ROLE)
def handle_get_chats():
    user = auth.current_user()
    name = clean_string(request.args.get("name"))
    chats = get_chats(account_id=user["account"].id, name=name)
    return jsonify([chat.to_dict() for chat in chats])


@chat_api.route("/api/chats", methods=["POST"])
@auth.login_required(role=USER_ROLE)
@expects_json(chat_schema)
def handle_add_chat():
    user = auth.current_user()
    name = clean_string(request.json["name"])
    model_type = request.json.get("model_type", app.config["DEFAULT_MODEL_TYPE"])
    instruction_prefix = clean_string(request.json.get("instruction_prefix"))
    user_prefix = clean_string(request.json.get("user_prefix"))
    assistant_prefix = clean_string(request.json.get("assistant_prefix"))
    account_id = user["account"].id
    chat = create_chat(
        name=name,
        account_id=account_id,
        model_type=model_type,
        instruction_prefix=instruction_prefix,
        user_prefix=user_prefix,
        assistant_prefix=assistant_prefix,
    )
    return jsonify(chat.to_dict()), 201


@chat_api.route("/api/chats/<int:chat_id>/messages", methods=["GET"])
@auth.login_required(role=USER_ROLE)
def handle_get_messages(chat_id):
    user = auth.current_user()
    account_id = user["account"].id
    check_account_chat(account_id=account_id, chat_id=chat_id)
    messages = get_messages(chat_id=chat_id)
    return jsonify([message.to_dict() for message in messages])


@chat_api.route("/api/chats/<int:chat_id>/messages", methods=["POST"])
@auth.login_required(role=USER_ROLE)
@expects_json(message_schema)
def handle_add_message(chat_id):
    user = auth.current_user()
    account_id = user["account"].id
    content = clean_string(request.json["content"])
    instruction = clean_string(request.json.get("instruction"))
    model_args = request.json.get("model_args", {})
    check_account_chat(account_id=account_id, chat_id=chat_id)
    message, over_soft_limit = ask(
        account=user["account"],
        chat_id=chat_id,
        content=content,
        instruction=instruction,
        model_args=model_args,
    )
    return jsonify({**message.to_dict(), "over_soft_limit": over_soft_limit}), 201

@chat_api.route("/api/chats/budget", methods=["GET"])
@auth.login_required(role=USER_ROLE)
def handle_get_usage():
    user = auth.current_user()
    account = user["account"]
    return jsonify({"usage": account.usage, "limit": account.budget})

@chat_api.route("/api/chats/<int:chat_id>/num_messages", methods=["GET"])
@auth.login_required(role=USER_ROLE)
def handle_get_num_messages(chat_id):
    user = auth.current_user()
    account_id = user["account"].id
    check_account_chat(account_id=account_id, chat_id=chat_id)
    num_messages = get_num_messages(chat_id=chat_id)
    return jsonify({"num_messages": num_messages})