import enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin

from utils import generate_uuid
from app import app

db = SQLAlchemy()


class MessageRoleType(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

    def __str__(self):
        return str(self.value)


class Base(db.Model, SerializerMixin):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"Base('{self.id}')"


class User(Base, SerializerMixin):
    serialize_rules = ("-account.users",)

    name = db.Column(db.Text, unique=False, nullable=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)

    def __repr__(self):
        return f"User('{self.name}')"


class Account(Base, SerializerMixin):
    serialize_rules = ("-users.account",)

    name = db.Column(db.String(80), unique=True, nullable=False)
    users = db.relationship("User", backref="account", lazy=True)
    api_key = db.Column(
        db.String(80), unique=True, nullable=False, default=generate_uuid
    )
    budget = db.Column(
        db.Integer, unique=False, nullable=False, default=app.config["DEFAULT_BUDGET"]
    )
    course = db.Column(db.String(80), unique=False, nullable=False)
    usage = db.Column(db.Integer, unique=False, nullable=False, default=0)
    active = db.Column(db.Boolean, unique=False, default=True)

    def __repr__(self):
        return f"Account('{self.name}')"


class Chat(Base, SerializerMixin):
    name = db.Column(db.String(80), unique=False, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False, index=True)
    model_type = db.Column(
        db.String(80),
        unique=False,
        nullable=True,
        default=app.config["DEFAULT_MODEL_TYPE"],
    )
    instruction_prefix = db.Column(
        db.Text,
        unique=False,
        nullable=True,
        default=app.config["DEFAULT_INSTRUCTION_PREFIX"],
    )
    user_prefix = db.Column(
        db.Text, unique=False, nullable=True, default=app.config["DEFAULT_USER_PREFIX"]
    )
    assistant_prefix = db.Column(
        db.Text,
        unique=False,
        nullable=True,
        default=app.config["DEFAULT_ASSISTANT_PREFIX"],
    )

    def __repr__(self):
        return f"Chat('{self.id}')"


class Message(Base, SerializerMixin):
    content = db.Column(db.Text)
    role = db.Column(db.Enum(MessageRoleType))
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"), nullable=False, index=True)
    model_args = db.Column(db.JSON, unique=False, nullable=True)
    usage = db.Column(db.JSON, unique=False, nullable=True)

    def __repr__(self):
        return f"Message('{self.id}')"
