from utils import Driver, Listener
import psycopg2

from flask import Flask
from flask_httpauth import HTTPBasicAuth
app = Flask(__name__)

def get_users():
    driver = Driver()
    driver.connect(mode='heroku')

@app.route("/")
def home():
    def listen():
        listener = Listener()
        listener.connect(mode='heroku')
        for item in listen:
            yield item
        return Response(listen(), mimetype='json')

@app.route("/auth")
@auth.login_required
def auth():
    return os.environ['DATABASE_URL']
