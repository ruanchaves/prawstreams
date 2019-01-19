from flask import Flask, jsonify, render_template
app = Flask(__name__)

from flask import render_template

@app.route('/test', methods=['GET'])
def test():
    input_json = { 'content' : [ { 'id' : 0, 'body' : '', 'author' : '', 'is_something' : True  } ],  'table' : 'stream' }
    restart_query = render_template('restart.sql.jinja2', **input_json)
    restart_query = jsonify(restart_query)
    insert_query = render_template('jsondump.sql.jinja2', **input_json)
    insert_query = jsonify(insert_query)
    dct = { 'restart' : restart_query, 'insert' : insert_query }
    return jsonify(dct)

@app.route('/')
def home():
    kwargs = { 'table' : 'test' , 'content' : [ { 'id' : 345 , 'value' : 'SERIAL PRIMARY KEY'}, {'id' : 485, 'value' : 'hahaha' } ] }
    return render_template('jsondump.sql.jinja2', **kwargs)
