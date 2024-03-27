# Parrot Backend Service

<!-- toc -->

- [Overview](#overview)
- [Account API](#account-api)
  * [**Get all accounts**](#get-all-accounts)
  * [**Create an account**](#create-an-account)
  * [**Update an account**](#update-an-account)
  * [**Delete an account**](#delete-an-account)
  * [**Get number of chats for an account**](#get-number-of-chats-for-an-account)
- [User API](#user-api)
  * [**Get all users**](#get-all-users)
  * [**Create a user**](#create-a-user)
- [Chat API](#chat-api)
  * [**Get all chats**](#get-all-chats)
  * [**Create a chat**](#create-a-chat)
  * [**Get all messages**](#get-all-messages)
  * [**Create (send) a message**](#create-send-a-message)
  * [**Get budget**](#get-budget)
  * [**Get number of messages for a chat**](#get-number-of-messages-for-a-chat)
- [Development](#development)
  * [Database](#database)
  * [Server](#server)
- [**Deployment**](#deployment)
  * [Docker](#docker)
  * [Deployment on AWS](#deployment-on-aws)

<!-- tocstop -->

## Overview
This service provides a REST API interface to interact with OpenAI models. Once deployed, you can talk to this service using an API tool such as [Postman](https://www.postman.com/) or simply `curl`. You need to be authenticated to use the service. If the API endpoint requires an admin access (e.g. user and account API), then admin token should be provided which is set at the time of service deployment (see Deployment) otherwise, account token (the API key assigned to the account) should be used. The authentication token should be provided in an `Authorization` header as a `Bearer` token such as `Authorization: Bearer <token>`. In Postman, you can easily add the token under the `Authorization` section by choosing `Bearer` type and inputting the token in the shown field.

## Account API
This API is used to manage accounts. Accounts can be also thought of as proxy accounts in OpenAI. They are automatically assigned a unique API key that can be used to interact with this API through GPT wrapper library. 
Note that this assigned key is *NOT* the OpenAI API key which is internal to this service and not shared with the users!

### **Get all accounts**
`GET /api/accounts`*

This endpoint returns all accounts. Following request parameters can be set for customized retrieval:
- `active` (bool, *optional*) - By default, this endpoint returns only the active accounts (i.e. not deleted accounts). If you want to retrieve deleted accounts, set `active` request parameter to `false` (i.e. `GET /api/accounts?active=false`).
- `usage` (int, *optional*) - Accounts below a certain usage can be filtered out with this parameter. For example, `GET /api/accounts?usage=1000` will return only those accounts that have used more than `1000` tokens.
- `name` (str, *optional*) - If you set this parameter, only accounts whose names contain the set value will be returned. For example, `GET /api/accounts?name=project` will return only those accounts that contain the string "project" in their names.

### **Create an account**
`POST /api/accounts`*

This endpoint creates a new account based on the given JSON data.
Available JSON fields are following:
- `name` (str, *required*) - Name of the account. Must be unique across accounts.
- `course` (str, *optional*) - Course assigned to the account.
- `budget` (int, *optional*) - Budget assigned to the account. Default value is defined in the config file. Budget is defined as the number of tokens an account is allowed to use.
- `users` (List[int], *optional*) - List of account users' IDs. These have to be valid IDs of users created using the `User` API.

Backend service automatically keeps track of the number of tokens used for an account (stored in the `usage` attribute) and denies access once the usage has reached the specified budget. It also warns the user once 75% of the budget has been spent.

### **Update an account**
`PUT /api/accounts/<account_id>`*

This endpoint updates attributes of the account specified by `account_id`. All mentioned attributes can be updated.

### **Delete an account**
`DELETE /api/accounts/<account_id>`*

This endpoint deletes an account (in reality, it sets the account `active` field to `False`). This effectively revokes the account access to the API.

### **Get number of chats for an account**
`GET /api/accounts/<account_id>/num_chats`*

This endpoint returns number of chats created by an account specified by the `account_id`.

## User API
This API is used to manage users. It is useful if you want to track of user information and their association with accounts.

### **Get all users**
`GET /api/users`*

This endpoint returns all users.

### **Create a user**
`POST /api/users`*

This endpoint creates a new user based on the given JSON data.
Available JSON fields are following:
- `code` (int, *required*) - Unique code for the user (typically student number or ID). Must be unique across users.
- `name` (str, *optional*) - Name of the user.
- `account_id` (str, *optional*) - ID of the account the user assigned to. Must be a valid account ID returned by Account API.

## Chat API
This API is used to interact with OpenAI API. It requires user (a.k.an account) authentication.

### **Get all chats**
`GET /api/chats`

This endpoint returns all the chats created by an account. It supports following request arguments:
- `name` (str, *optional*) - If set, only chats that contain the provided string in their names will be returned.

### **Create a chat**
`POST /api/chats`

This endpoint creates a new chat based on the given JSON data. This chat can be thought of a unique OpenAI chat session where you can send and receive several messages. Available JSON fields are the following:
- `name` (str, *required*) - Name of the chat.
- `model_type` (str, *optional*) - Type of the OpenAI model to use in this chat. Default value is defined in the config file. Currently, supported model types are `text_completion` and `chat_completion`.
- `instruction_prefix` (str, *optional*) - Prefix used to prepend to the instruction (a.k.a system) message in the OpenAI prompt. Only used for non-chat models such as GPT-3. Default value is defined in the config file.
- `user_prefix` (str, *optional*) - Prefix used to prepend to the user message in the OpenAI prompt. Only used for non-chat models such as GPT-3. Default value is defined in the config file.
- `assistant_prefix` (str, *optional*) - Prefix used to prepend to the assistant message in the OpenAI prompt. Only used for non-chat models such as GPT-3. Default value is defined in the config file.

### **Get all messages**
`GET /api/chats/<chat_id>/messages`

This endpoint returns all the messages sent in a chat specified by the `chat_id` and ordered by their creation time.

### **Create (send) a message**
`POST /api/chats/<chat_id>/messages`

This endpoint sends a new message in the chat specified by the `chat_id` based on the given JSON data. Note that prepending all the previous messages in the chat is handled by this service automatically, so all you need to send is the current message. Backend service also handles the usage and budget tracking. Available JSON fields are the following:
- `content` (str, *required*) - Content of the message.
- `instruction` (str, *optional*) - Optional system message to send before the actual message.
- `model_args` (json, *optional*) - A json object ssed to customize OpenAI model parameters (see OpenAI API for more details). Following attributes are available (default values for these parameters are defined in the config file.):
    - `temperature` - Temperature parameter.
    - `top_p` - Top p parameter.
    - `max_tokens` - Maximum number of tokens to generate. `null` means as many as the model generates before seeing a stop token.
    - `presence_penalty` - Presence penalty parameter.
    - `frequency_penalty` - Presence penalty parameter.

### **Get budget**
`GET /api/chats/budget`

This endpoint returns the budget and usage information for an account.

### **Get number of messages for a chat**
`GET /api/chats/<chat_id>/num_messages`

This endpoint returns the number of messages sent in a chat specified by the `chat_id`.

**requires admin authentication*

## Development

Install dependencies:
```sh
pip install -r requirements.txt
```

### Database
This service uses an SQL database and [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) to manage migrations and upgrades. Once you have deployed your database, you need to upgrade it to the latest version using `flask db` command (if you dont specify a database url, by default it creates a local sqlite database file):
```sh
FLASK_APP="server:init_app()" DATABASE_URL=<database url> flask db upgrade
```
If you are using a local Postgres instance, then the url is usually the following: `postgresql:///postgres`. To connect to this local db from Docker, use `postgresql://postgres@host.docker.internal:5432/postgres`.

To create a new database migration:
```sh
FLASK_APP="server:init_app()" DATABASE_URL=<database url> flask db migrate -m "migration message"
```

Flask-migrate is based on the popular SQLAlchemy database change management tool [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html). Check out its docs for more information.

### Server
To run the backend server, you need to specify the config file (by default, uses dev config `config.py`), server port (by default, uses 5000), the database URL, OpenAI API Key, and the admin token used to interact with the admin API (e.g. user and account API).
```sh
FLASK_APP="server:init_app()" FLASK_RUN_PORT=8080 FLASK_CONFIG=prod_config.py FLASK_DEBUG=True OPENAI_API_KEY=<API KEY> PARROT_ADMIN_TOKEN=<ADMIN TOKEN> DATABASE_URL=<database url> flask run
```

## **Deployment**

### Docker

This backend service can be run and deployed as a docker container as well with the provided Dockerfile. This dockerfile uses gunicorn server which is meant for production use and allows you to configure number of threads and workers. You need to pass the environment variables as docker environment variables:

Build the docker image:
```sh
docker build . -t parrot-backend
```

Run the docker image:
```sh
docker run -p 8080:8080 -it -d -e "FLASK_APP=server:init_app()" -e "FLASK_RUN_PORT=8080" -e "FLASK_CONFIG=prod_config.py" -e "FLASK_DEBUG=False" -e "OPENAI_API_KEY=<OpenAI API Key>" -e "PARROT_ADMIN_TOKEN=<admin token>" -e "DATABASE_URL=<database url>" parrot-backend
```

### Deployment on AWS

If you are using AWS Cloud, you can deploy the docker image in Elastic Container Registry and launch it using [Elastic Container Service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html).

Follow [AWS CLI Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) to install and configure AWS CLI for the first time.

Create a repository on ECR first (e.g. named backend-service).

Login to AWS Elastic Container Registry:
```sh
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

Build the docker image:
```sh
docker build . -t <account-id>.dkr.ecr.<region>.amazonaws.com/parrot-backend
```

Push docker image:
```sh
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/parrot-backend
```