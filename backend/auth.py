import os

from flask import jsonify
from flask_httpauth import HTTPTokenAuth
from database import Account
from sqlalchemy.sql import select
from database import db

USER_ROLE = "user"
ADMIN_ROLE = "admin"
ADMIN_TOKEN = os.getenv("PARROT_ADMIN_TOKEN")

auth = HTTPTokenAuth()


@auth.get_user_roles
def get_user_roles(user):
    return user["role"]


@auth.error_handler
def auth_error(status):
    return jsonify({"error": "Access Denied"}), status


@auth.verify_token
def verify_token(token):
    if token == ADMIN_TOKEN:
        return {"role": ADMIN_ROLE}

    stmt = select(Account).where((Account.api_key == token) & (Account.active == True))
    account = db.session.scalars(stmt).one_or_none()

    if account:
        return {"role": USER_ROLE, "account": account}
