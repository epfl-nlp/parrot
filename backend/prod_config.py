import os

basedir = os.path.abspath(os.path.dirname(__file__))

FLASK_ENV = "production"
FLASK_DEBUG = os.getenv("FLASK_DEBUG", False)

# Database config
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# OpenAI config
DEFAULT_BUDGET = 1e7
DEFAULT_MODEL_TYPE = "chat_completion"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MODEL_ARGS = {
    "temperature": 0.7,
    "top_p": 1.0,
    "max_tokens": None,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "best_of": 1,
}
DEFAULT_TEXT_COMPLETION_MODEL = "text-davinci-003"
DEFAULT_CHAT_COMPLETION_MODEL = "gpt-3.5-turbo"
DEFAULT_INSTRUCTION_PREFIX = "My request: "
DEFAULT_USER_PREFIX = "My request: "
DEFAULT_ASSISTANT_PREFIX = "Your response: "
