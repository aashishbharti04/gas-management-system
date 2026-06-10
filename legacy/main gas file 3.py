import mysql.connector as sql , datetime as dt
import datetime
conn=sql.connect(host='localhost',user='root',passwd='ADMINISTRATOR12345',database='gasin')
if conn.is_connected():
    print("connected")
mycursor=conn.cursor()
#mycursor.execute("create table gasin(v_customer varchar(30) primary key , v_accno bigint,v_date date,v_add varchar(40), v_cng bigint, v_lpg bigint, v_debit bigint,v_amtobe_paid bigint , v_credit bigint")
print("..............GAS INVENTORY MANAGEMENT SYSTEN.............")
print("..............GAS INVENTORY MANAGEMENT SYSTEN.............")
#mycursor.execute("create table user ( username varchar(10) not null primary key, password varchar(10))")
#print("table is created")
username=input("ENTER THE YOUR USERNAME:")
password=input("ENTER YOUR PASSWORD IN 10  CHARACRTER : ")
if username ==akash and password ==akash06060:
    print ("USER IS IDENTIFIED")

else:
    quit
for i in range (0,99999999999):    
    print("1.CREATE ACCOUNT")
    print("2.TO MAKE BILL")
    print("3.TO GET DETAILS OF THE CUSTOMER")
    print("4.TO GET THE DETAILE OF EVERY CUSTOMER")
    print("5.TO GET DETAILS OF A PARTICULAR CUSTOMER")
    print("6.TOINSERT MULTIPLE VALUES")
    print("7.enter 0 to log out")
    choice=int(input("enter your choice as per the above information:"))
    if choice==1:
        v_customer=input("enter the name customer ")
        v_accno=input("enter your account  number:")
        v_date=datetime.datetime.now()
        v_add=input("enter your complete address:")
        v_debit=input("enter your debit card number:")
        v_credit=int(input("enter your credit amount:"))
        mycursor.execute("insert into gasin values('{}' , '{}' , {} , '{}' , '{}' , '{}' )".format(v_customer , v_accno ,  v_date, v_add  , v_debit ,  v_credit  ))
        print ("äccount is created")
        print("_______________________________________________________________________________")
conn.commit()
