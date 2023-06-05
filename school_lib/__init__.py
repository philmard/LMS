import mysql.connector
from flask import Flask


app = Flask(__name__)
app.secret_key = '2002'
# Connect to the MySQL database
connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='school_lib'
)

from school_lib import routes