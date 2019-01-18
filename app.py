import os
from flask import Flask, Response, request, jsonify
from flask_httpauth import HTTPBasicAuth
from utils import Driver, Listener
import json
app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    'prawstreams' : 'prawstreams'
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/auth')
@auth.login_required
def auth():
    database_key = os.environ.get('DATABASE_URL')
    return database_key

@app.route('/')
def fetch():
    def listen():
        listener = Listener()
        listener.connect(mode='heroku')
        for item in listener:
            yield json.dumps(item)
    return Response(listen(),mimetype='json')

@app.route('/accounts',methods=['POST', 'GET'])
def accounts():
    driver = Driver()
    driver.connect(mode='heroku')
    if request.method != "POST":
        result = driver.pull('select * from accounts')
        return json.dumps(result)
    else:
        input_json = request.get_json(force=True)
        template = open('jsonexport.sql').read() 
        dct = {'sucess' : 42}
        return jsonify(dct)

if __name__ == '__main__':
    app.run()
