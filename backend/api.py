from typing import List, Tuple
from sqlalchemy import select, func

from database import db, User, Account, Chat, Message, MessageRoleType
from gpt import ask_chatgpt, ask_gpt3, MODEL_TYPES, GPTError, check_model_args


class APIException(Exception):
    pass


def get_account(account_id: int) -> Account:
    stmt = select(Account).where((Account.id == account_id) & (Account.active == True))
    account = db.session.scalars(stmt).one_or_none()

    if not account:
        raise APIException(f"Account with id {account_id} does not exist")

    return account


def create_user(code: str, account_id: int = None, name: str = None) -> User:
    stmt = select(User).where(User.code == code)
    user = db.session.scalars(stmt).one_or_none()

    if user:
        raise APIException(f"User with code {code} already exists")

    if account_id:
        get_account(account_id)

    user = User(name=name, code=code, account_id=account_id)
    db.session.add(user)
    db.session.commit()

    return user


def get_users() -> List[User]:
    stmt = select(User).order_by(User.code)
    users = db.session.scalars(stmt).all()
    return users


def create_account(
    name: str,
    budget: int,
    course: str,
    user_ids: List[int] = None,
    api_key: str = None,
) -> Account:
    stmt = select(Account).where(Account.name == name)
    account = db.session.scalars(stmt).one_or_none()

    if account:
        raise APIException(f"Account with name {name} already exists")

    users = []

    if users:
        for user_id in user_ids:
            stmt = select(User).where(User.id == user_id)
            user = db.session.scalars(stmt).one_or_none()

            if not user:
                raise APIException(f"User with id {user_id} does not exist")

            users.append(user)

    account = Account(
        name=name, api_key=api_key, budget=budget, course=course, users=users
    )
    db.session.add(account)
    db.session.commit()

    return account


def update_account(
    account_id: int,
    name: str = None,
    budget: int = None,
    course: str = None,
    user_ids: List[int] = None,
) -> Account:
    account = get_account(account_id)

    if name is not None:
        account.name = name

    if budget is not None:
        account.budget = budget

    if course is not None:
        account.course = course

    if user_ids is not None:
        users = []

        for user_id in user_ids:
            stmt = select(User).where(User.id == user_id)
            user = db.session.scalars(stmt).one_or_none()

            if not user:
                raise APIException(f"User with id {user_id} does not exist")

            users.append(user)

        account.users = users

    db.session.commit()

    return account


def get_accounts(active: bool = True, usage: int = None, name: str = None) -> List[Account]:
    try:
        if usage is not None:
            usage = int(usage)
    except (ValueError, TypeError):
        raise APIException(f"Usage {usage} is not a valid integer")

    stmt = select(Account).where(Account.active == active).order_by(Account.name)

    if name is not None:
        stmt = stmt.where(Account.name.icontains(name, autoescape=True))
    
    if usage is not None:
        stmt = stmt.where(Account.usage > usage)

    accounts = db.session.scalars(stmt).all()
    return accounts


def delete_account(account_id: int) -> Account:
    stmt = select(Account).where(Account.id == account_id)
    account = db.session.scalars(stmt).one_or_none()

    if not account:
        raise APIException(f"Account with id {account_id} does not exist")

    account.active = False
    db.session.commit()

    return account


def get_chats(account_id: int, name: str = None) -> List[Chat]:
    if name is not None:
        stmt = (
            select(Chat)
            .where(
                (Chat.account_id == account_id) & (Chat.name.icontains(name, autoescape=True))
            )
            .order_by(Chat.id)
        )
    else:
        stmt = select(Chat).where(Chat.account_id == account_id).order_by(Chat.id)
    chats = db.session.scalars(stmt).all()
    return chats


def get_messages(chat_id: int) -> List[Message]:
    stmt = (
        select(Message).where(Message.chat_id == chat_id).order_by(Message.id)
    )
    messages = db.session.scalars(stmt).all()
    return messages


def create_chat(
    name: str,
    account_id: int,
    model_type: str,
    instruction_prefix: str = None,
    user_prefix: str = None,
    assistant_prefix: str = None,
) -> Chat:
    if model_type not in MODEL_TYPES:
        raise APIException(f"Model type {model_type} is not supported")

    get_account(account_id)

    chat = Chat(
        name=name,
        account_id=account_id,
        model_type=model_type,
        instruction_prefix=instruction_prefix,
        user_prefix=user_prefix,
        assistant_prefix=assistant_prefix,
    )
    db.session.add(chat)
    db.session.commit()

    return chat


def create_message(
    content: str,
    role: str,
    chat_id: int,
    model_args: dict = None,
    usage: dict = None,
    commit: bool = True,
) -> Message:
    stmt = select(Chat).where(Chat.id == chat_id)
    chat = db.session.scalars(stmt).one_or_none()

    if not chat:
        raise APIException(f"Chat with id {chat_id} does not exist")

    if not model_args:
        model_args = {}

    if not usage:
        usage = {}

    message = Message(
        content=content, role=role, chat_id=chat_id, model_args=model_args, usage=usage
    )
    db.session.add(message)

    if commit:
        db.session.commit()

    return message


def get_chat(chat_id: int) -> Chat:
    stmt = select(Chat).where(Chat.id == chat_id)
    chat = db.session.scalars(stmt).one_or_none()

    if not chat:
        raise APIException(f"Chat with id {chat_id} does not exist")

    return chat


def check_account_chat(account_id: int, chat_id: int) -> Chat:
    stmt = select(Chat).where(Chat.id == chat_id)
    chat = db.session.scalars(stmt).one_or_none()

    if not chat:
        raise APIException(f"Chat with id {chat_id} does not exist")

    if chat.account_id != account_id:
        raise APIException(f"Chat with id {chat_id} does not belong to account {account_id}")

    return chat


def ask(
    account: Account,
    chat_id: int,
    content: str,
    instruction: str = None,
    model_args: dict = None,
) -> Tuple[Message, bool]:
    try:
        over_soft_limit = False

        if account.usage >= account.budget:
            raise APIException("Account has reached its budget")

        if account.usage >= account.budget * 0.75:
            over_soft_limit = True

        model_args = check_model_args(model_args)
        chat = get_chat(chat_id)
        messages = get_messages(chat_id)

        if instruction:
            instruction_msg = create_message(
                content=instruction,
                role=MessageRoleType.SYSTEM,
                chat_id=chat_id,
                commit=False,
            )
            messages.append(instruction_msg)

        request_msg = create_message(
            content=content, role=MessageRoleType.USER, chat_id=chat_id, commit=False
        )
        messages.append(request_msg)

        if chat.model_type == "chat_completion":
            gpt_response = ask_chatgpt(chat, messages, model_args=model_args)
        else:
            gpt_response = ask_gpt3(chat, messages, model_args=model_args)

        account.usage += gpt_response.usage["total_tokens"]
        response_msg = create_message(
            content=gpt_response.content,
            role=MessageRoleType.ASSISTANT,
            chat_id=chat_id,
            model_args=gpt_response.model_args,
            usage=gpt_response.usage,
            commit=False,
        )

        db.session.commit()

        return response_msg, over_soft_limit
    except GPTError as e:
        raise APIException(str(e))


def get_num_chats(account_id: int) -> int:
    stmt = select(func.count(Chat.id)).where(Chat.account_id == account_id)
    num_chats = db.session.scalars(stmt).one()
    return num_chats


def get_num_messages(chat_id: int) -> int:
    stmt = select(func.count(Message.id)).where(Message.chat_id == chat_id)
    num_messages = db.session.scalars(stmt).one()
    return num_messages