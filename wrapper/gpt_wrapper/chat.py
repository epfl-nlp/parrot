from typing import List
import warnings

from gpt_wrapper import APIException, API, get_json, get_error_message


class Message:
    def __init__(
        self,
        message_id: int,
        chat_id: int,
        content: str,
        role: str,
        created_at: str = None,
        usage: dict = None,
        model_args: dict = None,
    ):
        self.message_id = message_id
        self.chat_id = chat_id
        self.content = content
        self.role = role
        self.created_at = created_at
        self.usage = usage
        self.model_args = model_args

    def __str__(self):
        return f"{self.content}"

    def to_dict(self) -> dict:
        """Generate a dictionary representation of the message.

        Returns:
            dict: Dictionary representation of the message.
        """
        return {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "content": self.content,
            "role": self.role,
            "created_at": self.created_at,
            "usage": self.usage,
            "model_args": self.model_args,
        }


class Chat:
    def __init__(
        self,
        chat_id: int,
        name: str = None,
        created_at: str = None,
        model_type: str = None,
        instruction_prefix: str = None,
        user_prefix: str = None,
        assistant_prefix: str = None,
    ):
        self.chat_id = chat_id
        self.name = name
        self.created_at = created_at
        self.model_type = model_type
        self.instruction_prefix = instruction_prefix
        self.user_prefix = user_prefix
        self.assistant_prefix = assistant_prefix

    def __str__(self):
        return f"{self.name} ({self.chat_id})"

    def to_dict(self) -> dict:
        """
        Generate a dictionary representation of the chat.

        Returns:
            dict: Dictionary representation of the chat.
        """
        return {
            "chat_id": self.chat_id,
            "name": self.name,
            "created_at": self.created_at,
            "model_type": self.model_type,
            "instruction_prefix": self.instruction_prefix,
            "user_prefix": self.user_prefix,
            "assistant_prefix": self.assistant_prefix,
        }

    @classmethod
    def list(cls, name: str = None) -> List["Chat"]:
        """List all chats.

        Args:
            name (str, optional): Filter by name. Defaults to None.

        Raises:
            APIException: If the API returns an error.

        Returns:
            List[Chat]: List of chats.
        """
        api = API()
        response = api.get("/api/chats", params={"name": name})

        if response.status_code != 200:
            raise APIException(get_error_message(response))

        response_json = get_json(response)

        return [
            cls(
                chat_id=res["id"],
                name=res["name"],
                created_at=res["created_at"],
                model_type=res["model_type"],
                instruction_prefix=res["instruction_prefix"],
                user_prefix=res["user_prefix"],
                assistant_prefix=res["assistant_prefix"],
            )
            for res in response_json
        ]

    @classmethod
    def create(
        cls,
        name: str,
        model_type: str = "chat_completion",
        instruction_prefix: str = None,
        user_prefix: str = None,
        assistant_prefix: str = None,
    ) -> "Chat":
        """
        Create a new chat.

        Args:
            name (str): Name of the chat.
            model_type (str, optional): Type of model to use. Defaults to "chat_completion".
            instruction_prefix (str, optional): Prefix to use for instructions. Defaults to None.
            user_prefix (str, optional): Prefix to use for user messages. Defaults to None.
            assistant_prefix (str, optional): Prefix to use for assistant messages. Defaults to None.

        Raises:
            APIException: If the API returns an error.

        Returns:
            Chat: The created chat.
        """
        data = {"name": name, "model_type": model_type}

        if instruction_prefix:
            data["instruction_prefix"] = instruction_prefix

        if user_prefix:
            data["user_prefix"] = user_prefix

        if assistant_prefix:
            data["assistant_prefix"] = assistant_prefix

        api = API()
        response = api.post("/api/chats", json=data)

        if response.status_code != 201:
            raise APIException(get_error_message(response))

        response_json = get_json(response)

        return cls(
            chat_id=response_json["id"],
            name=response_json["name"],
            created_at=response_json["created_at"],
            model_type=response_json["model_type"],
            instruction_prefix=response_json["instruction_prefix"],
            user_prefix=response_json["user_prefix"],
            assistant_prefix=response_json["assistant_prefix"],
        )

    def messages(self) -> List[Message]:
        """
        List all messages in the chat.

        Raises:
            APIException: If the API returns an error.

        Returns:
            List[Message]: List of messages.
        """
        api = API()
        response = api.get(f"/api/chats/{self.chat_id}/messages")
        
        if response.status_code != 200:
            raise APIException(get_error_message(response))

        response_json = response.json()

        return [
            Message(
                message_id=res["id"],
                chat_id=res["chat_id"],
                content=res["content"],
                role=res["role"],
                created_at=res["created_at"],
                usage=res["usage"],
                model_args=res["model_args"],
            )
            for res in response_json
        ]

    def ask(
        self, content: str, instruction: str = None, model_args: dict = None
    ) -> Message:
        """
        Ask the assistant a question.

        Args:
            content (str): Content of the message.
            instruction (str, optional): Instruction to use. Defaults to None.
            model_args (dict, optional): Model arguments to use. Defaults to None.

        Raises:
            APIException: If the API returns an error.

        Returns:
            Message: The created message.
        """
        data = {"content": content}

        if instruction:
            data["instruction"] = instruction

        if model_args:
            data["model_args"] = model_args

        api = API()
        response = api.post(
            f"/api/chats/{self.chat_id}/messages",
            json=data,
        )
        
        if response.status_code != 201:
            raise APIException(get_error_message(response))

        response_json = response.json()

        if response_json["over_soft_limit"]:
            warnings.warn("You have passed the 75% of your allocated budget.")

        return Message(
            message_id=response_json["id"],
            chat_id=response_json["chat_id"],
            content=response_json["content"],
            role=response_json["role"],
            created_at=response_json["created_at"],
            usage=response_json["usage"],
            model_args=response_json["model_args"],
        )
    
    @classmethod
    def budget(cls):
        """
        Get the budget details.

        Raises:
            APIException: If the API returns an error.

        Returns:
            dict: Budget details.
        """
        api = API()
        response = api.get(f"/api/chats/budget")

        if response.status_code != 200:
            raise APIException(get_error_message(response))

        response_json = response.json()

        return response_json
