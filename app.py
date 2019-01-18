import os
from flask import Flask, Response, request, jsonify
from utils import Driver, Listener
import json

app = Flask(__name__)

def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/auth')
def auth():
    database_key = os.environ.get('DATABASE_URL')
    return jsonify( { 'URI' : database_key } )

@app.route('/')
def fetch():
    def listen():
        listener = Listener()
        listener.connect(mode='heroku')
        for item in listener:
            yield json.dumps(item)
    return Response(listen(),mimetype='json')

@app.route('/pull/<variable>',methods=['GET'])
def pull(variable):
    driver = Driver()
    driver.connect(mode='heroku')
    query = 'select row_to_json({0}) from {0}'.format(variable)
    result = driver.pull(query)
    result = [ x for t in result for x in t ]
    output_dct = { 'content' : result }
    return jsonify(output_dct)

@app.route('/push',methods=['POST'])
def push():
    driver = Driver()
    driver.connect(mode='heroku')
    input_json = request.get_json(force=True)
    query = render_template('jsondump.sql.jinja2', **input_json)
    driver.push(query)

@app.route('/overwrite/<variable>',methods=['POST'])
def overwrite(variable):
    driver = Driver()
    driver.connect(mode='heroku')
    input_json = request.get_json(force=True)
    input_json['table'] = variable
    restart_query = render_template('restart.sql.jinja2', **input_json)
    insert_query = render_template('jsondump.sql.jinja2', **input_json)
    driver.push(restart_query)
    driver.push(insert_query)

@app.route('/test', methods=['GET'])
def test():
    input_json = { 'content' : { 'id' : 0, 'body' : '', 'author' : '', 'is_something' : true  } ,  'table' : 'stream' }
    print(json.dumps(input_json))
    restart_query = render_template('restart.sql.jinja2', **input_json)
    print(restart_query)
    insert_query = render_template('jsondump.sql.jinja2', **input_json)
    print(insert_query)
    dct = { 'restart' : restart_query, 'insert' : insert_query }
    return jsonify(dct)

if __name__ == '__main__':
    app.run()
