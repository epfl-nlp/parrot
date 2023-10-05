# Parrot GPT Wrapper

<!-- toc -->

- [Overview](#overview)
- [Setup](#setup)
- [API](#api)
  * [Chat API](#chat-api)
- [Development](#development)

<!-- tocstop -->

## Overview
This is a python library to provide students with OpenAI wrapper interface through our API. Students can use this library to interact with OpenAI models such as GPT-3 and ChatGPT for free (paid by instructors!). 

## Setup
Library can be installed from the wheel provided under the [artifacts](/artifacts) folder as below:

```sh
pip install artifacts/gpt_wrapper-0.1.0-py3-none-any.whl
```

The minimum required python version for this package is `3.8`.

In order to use the wrapper, users need to be authenticated using an API key assigned to them by us that is created when an account is created (Account API returns this API key when a new account is created). API key can be set similar to OpenAI API as below:
```python
import gpt_wrapper

gpt_wrapper.api_key = "<API key>"
```
This key can also be set using the environment variable `PARROT_API_KEY`.

By default, this library tries to connect to the backend API at `http://localhost:5000` (you can change this default value in the `gpt_wrapper/__init__.py`). To configure this from the installed library, either set it in the code as below:
```python
import gpt_wrapper

gpt_wrapper.api_base = "<API base URL>"
```
This url can also be set using the environment variable `PARROT_API_BASE`.

## API

### Chat API
You can create a new chat session using the `Chat` interface.
```python
from gpt_wrapper.chat import Chat

chat = Chat.create("Test Chat")
```
By default, chat is connected to the `chat_completion` models of OpenAI such as `gpt-3.5-turbo`

Alternatively, you can configure the model type and prefixes used to construct the prompt for `text_completion` models such as `text-davinci-003`.

```python
from gpt_wrapper.chat import Chat

chat = Chat.create(
    name="Test Chat",   # required
    model_type="text_completion",  # optional, defaults to `chat_completion`
    instruction_prefix="Instruction: ",  # optional, defaults to "My request: "
    user_prefix="User: ",   # optional, defaults to "My request:"
    assistant_prefix="Assistant: "  # optional, defaults to "Your response: "
)
```
Note that prefixes are only used for `text_completion` models. Returned `Chat` object has the following fields: `chat_id`, `name`, `created_at`, `model_type`, `instruction_prefix`, `user_prefix`, `assistant_prefix`.

You can also list all chats:
```python
chats = Chat.list()
```

If you would like to retrieve chats by name, you can pass it as a parameter:
```python
chats = Chat.list(name="test")
```
Note that this is not an exact match, it will return all chats whose names contain "test".

`Chat` object can be converted to a dictionary as below:
```python
chat.to_dict()
```

To ask the GPT model a question, you can use the `ask` method of the `Chat` object.

```python
message = chat.ask("Who won the world series in 2020?")
print(message)
```

You can also provide an instruction separately to the model:
```python
message = chat.ask("Who won the world series in 2020?", instruction="You are a helpful assistant.")
print(message)
```

Optionally, model arguments can be configured as well:
```python
message = chat.ask("Who won the world series in 2020?",
                   model_args={
                        "temperature": 0.7,
                        "max_tokens": 100,
                        "top_p": 0.9,
                        "presence_penalty": 0.1,
                        "frequency_penalty": 0.1
                   })
print(message)
```

Consult [OpenAI API Documentation](https://platform.openai.com/docs/introduction) for more details on these parameters. By default, these parameters have been set to reasonably good values that can be checked by `Message` fields. 

Message object has the following fields available:
- `message_id` - Message's unique ID.
- `chat_id` - The chat session ID the message belongs to.
- `content`- The message content.
- `role` - There are three options for role:
    - `user` - The user role belongs to you.
    - `assistant` - The assistant role belongs to the OpenAI model.
    - `system` - The system role belongs to the system-level instruction that you can pass with the instruction parameter in `ask`.
- `created_at` - The time the message was created
- `usage` - Number of tokens used to generate this message, only set for "assistant" messages.
- `total_tokens` - Total input and output tokens the message has used.
- `prompt_tokens` - Number of tokens your input has used.
- `completion_tokens` - Number of tokens the OpenAI model has generated.
- `model_args`: Arguments passed to OpenAI API to produce this message, only set for "assistant" message.

You can also retrieve all messages sent to a chat as below:
```python
messages = chat.messages()
print([str(message) for message in messages])
```

`Message` object can be converted to a dictionary as below:
```python
message.to_dict()
```

To track your API key's overall token usage and budget, you can do the following command:
```python
budget = Chat.budget()
print(budget)
# {'limit': 100000000, 'usage': 4062003}
```

In this output:
- `limit` shows that you have a total limit of 10 million tokens.
- `usage` shows that across all chats you have spent ~4 million tokens.

## Development

This library uses [poetry](https://python-poetry.org/) for dependency managemenet and packaging. Follow installation [documentation](https://python-poetry.org/docs/#installation) to install poetry. Then you can run the following to install packages:
```sh
poetry install
```

Note that this library doesn't use setuptools for package configuration and instead uses latest standard which is pyproject.toml. 
If you modify or add a new dependency in this file, then you need to update the poetry lock file to reflect the changes. Run the following command for this:
```sh
poetry update
```

To build the distribution package, run the build command as follows:
```sh
poetry build -f wheel
```

This command will build and output the package in `dist` folder (not checked into git, but the latest version can be found in [artifacts](/artifacts) folder). This package can be installed using pip:
```sh
pip install artifacts/gpt_wrapper-0.1.0-py3-none-any.whl
```