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

@app.route('/pull/<variable>',methods=['GET'])
def pull():
    driver = Driver()
    driver.connect(mode='heroku')
    input_json = request.get_json(force=True)
    query = 'select row_to_json({0}) from {0}'.format(input_json['table'])
    try:
        result = driver.pull(query)
    except Exception as e:
        return { 'status' : 400, 'exception' : e }
    result = [ x for t in result for x in t ]
    output_dct = { 'content' : result , 'table' : input_json['table'] }
    return jsonify(output_dct)

@app.route('/push',methods=['POST'])
def push():
    driver = Driver()
    driver.connect(mode='heroku')
    input_json = request.get_json(force=True)
    query = render_template('jsondump.sql.jinja2', **input_json)
    try:
        driver.push(query)
        return { 'status' : 200 }
    except Exception as e:
        return { 'status' : 400, 'exception' : e }

@app.route('/overwrite',methods=['POST'])
def overwrite():
    driver = Driver()
    driver.connect(mode='heroku')
    input_json = request.get_json(force=True)
    restart_query = render_template('restart.sql.jinja2', **input_json)
    insert_query = render_template('jsondump.sql.jinja2', **input_json)
    try:
        driver.push(restart_query)
        driver.push(insert_query)
        return { 'status' : 200 }
    except Exception as e:
        return { 'status' : 400, 'exception' : e }

if __name__ == '__main__':
    app.run()
