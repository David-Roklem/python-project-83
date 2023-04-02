import os
from flask import Flask
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY)


@app.route('/')
def index():
    return '<h1>Hello, the third project. Be kind to your lord!</h1>'
