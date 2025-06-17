import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # <-- db password
    database="" # <-- db name
)
