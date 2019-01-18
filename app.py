import os
from flask import Flask
app = Flask(__name__)

@app.route('/')
def auth():
    database_key = os.environ.get('DATABASE_URL')
    return 'Database key: {0}'.format(database_key)

if __name__ == '__main__':
    app.run()
# from utils import Driver, Listener
# import psycopg2

# from flask import Flask
# from flask_httpauth import HTTPBasicAuth
# app = Flask(__name__)

# def get_users():
#     driver = Driver()
#     driver.connect(mode='heroku')

# @app.route("/")
# def home():
#     return 'hello world'
#     # def listen():
#     #     listener = Listener()
#     #     listener.connect(mode='heroku')
#     #     for item in listen:
#     #         yield item
#     #     return Response(listen(), mimetype='json')

# @app.route("/auth")
# @auth.login_required
# def auth():
#     return os.environ['DATABASE_URL']
