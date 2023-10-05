import os

from flask import Flask

app = Flask(__name__)
app.config.from_pyfile(os.getenv("FLASK_CONFIG", "config.py"))
