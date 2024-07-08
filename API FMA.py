# API creation for FMA database
# intialise the API in the workbook before we use the SQL data base to expose the data

from flask import Flask, request, jsonify
from collections import defaultdict
import pymysql.cursors


app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kaiser123',
    'database': 'FMA',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/')
def home():
    return "Welcome to Nabil's Music API based on FMA dataset"
@app.route('/tracks',method=['GET'])
def track_function():
    