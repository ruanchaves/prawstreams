from utils import Driver
import psycopg2

from flask import Flask
from flask_httpauth import HTTPBasicAuth
app = Flask(__name__)

def get_users():
    driver = Driver()
    driver.connect(mode='heroku')

@app.route("/")
def home():
    pass

@app.route("/auth")
@auth.login_required
def auth():
    return 'hello'
