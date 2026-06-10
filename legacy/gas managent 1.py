import mysql.connector as sql
conn=sql.connect(host='localhost',user='root',passwd='ADMINISTRATOR12345',database='gasin')
if conn.is_connected():
    print("connected")
mycursor=conn.cursor()
mycursor.execute("create table gasin(v_customer varchar(30) primary key , v_accno bigint,v_date date,v_add varchar(40), v_cng bigint, v_lpg bigint, v_debit bigint,v_amtobe_paid bigint , v_credit bigint")
