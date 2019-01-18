from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/')
def home():
    kwargs = { 'table' : 'test' , 'content' : [ { 'id' : 345 , 'value' : 'SERIAL PRIMARY KEY'}, {'id' : 485, 'value' : 'hahaha' } ] }
    return render_template('jsondump.sql.jinja2', **kwargs)
