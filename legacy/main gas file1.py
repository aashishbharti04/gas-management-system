import mysql.connector as sql , datetime as dt
import datetime
conn=sql.connect(create database gasin)
if conn.is_connected():
    print("connected")
mycursor=conn.cursor()
conn.commit()
