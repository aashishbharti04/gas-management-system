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
username=input("ENTER THE YOUR USERNAME TO LOGIN TO THE SOFTWARE:")
password=input("ENTER YOUR PASSWORD IN 10  CHARACRTER TO LOGIN TO THE SOFTWARE : ")
if username =='akash' and password =='akash06060':
    print ("                      USER IS IDENTIFIED                            ")
    print ("                                                                                                   ")
    print ("_____________________________________________________________________________________________")
    print("                                                                                                                                                                                                 ")
    print("                                                                                                                                                                                                 ")
    print ("                     YOU CAN PROCEED                                  ") 
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
            mycursor.execute("insert into gasin values('{}' , {} , {} , '{}' , {} , {} )".format(v_customer , v_accno ,  v_date, v_add  , v_debit ,  v_credit  ))
            print ("äccount is created")
            print("_______________________________________________________________________________")
            print("                                                                                                                                                                                                 ")
            print("                                                                                                                                                                                                 ")
            
            continue                                           
        elif choice==2:
            mycursor.execute("select * from gasin")
            re=mycursor.fetchall()
            print("YOUR RESULT IS ")
            for x in re:
                print(x)
                print("_______________________________________________________________________________")
                print("                                                                                                                                                                                                 ")
                print("                                                                                                                                                                                                 ")
                continue
        elif choice == 3:        
            customer_name=input("ENTER THE NAME OF CUSTOMER:")
            import datetime
            v_date=datetime.datetime.now()
            date = v_date
            print("the date & time is:",v_date)
            print("CHOOSE A CHOICE FROM THE FOLLOWING AS PER THE GAS IS BOUGHT BY THE CUSTOMER:")
            print("1. C N G ......Rs.75/l")
            print("2.L P G .......Rs.80/l")
            print("3.both LPG.....Rs.75/l & CNG.... Rs.80/l")
            print("                                                                                                                                                                                                 ")
            ch=int(input("enter your choice:"))
            print("                                                                                                                                                                                                 ")
            print("                                                                                                                                                                                                 ")
            if ch==1:
                cng=int(input("enter the quantity bought:"))
                amount= 75*cng
                print("THE AMOUNT TO BE PAID IS :",amount)
                mycursor.execute("update gasin set v_cng='cng',v_amtobe_paid='amont',where customer ='customer_name'")
                cho=int(input("if transaction is to be done through the credit amount enter 1:"))
                if cho==1:
                    remaining=v_credit-amount
                    mycursor.execute ("updata gasin set v_credit=('remaining'),v_date=('date') where v_customer='customer_name'")
                    print("your record is updated")
                else:
                    print("INVALID CODE")
            if ch==2:
                lpg=int(input("enter the amount bought by the customer:"))
                pay = 80*lpg
                print("the amount to be is: ",pay)
                mycursor.execute("update gasin set v_lpg='lpg',v_amtobe_paid='pay' where v_customer='customer_name'")
                print("your record is updated")
                choo=int(input("if transaction is to be done through the credit amount enter 1:"))    
                if choo==1:
                    remain=v_credit-pay
                    mycursor.execute("update gasin set v_credit='remain',v_date='date'where v_customer ='customer_name'")
                    print("your record is updated")
                    print("                                                                                                                                                                                                 ")
                    print("                                                                                                                                                                                                 ")
            if ch==3:
                lpgas=int(input("enter the amount of LPG GAS bought:"))
                cngas=int(input("enter the amount of CNG GAS bought:"))
                total=80*lpgas+75*cngas
                print("the amount to be is: ",total)
                mycursor.execute("update gasin set v_lpg='lpgas',v_cng='cngas',v_amtobe_paid='total' where v_customer='customer_name'")
                print("your record is updated")

                chio=int(input("if transaction is to be done through the credit amount enter 1:"))
                
                if chio==1:
                    remaind=v_credit-total
                    mycursor.execute("update gasin set v_credit='remaind',v_date='date'where v_customer ='customer_name'")
            else:
                print ("<<<<<<  .............IT IS INVALID CODE..........>>>>>>>>>>>")
                print("<<<<<<<...........Re-enter the suitable code........>>>>>>>>>>>")
                print("________________________________________________________________________________________________________________________")
                print("                                                                                                                                                                                                 ")
                print("                                                                                                                                                                                                 ")
                continue
        elif choice==4:
            mycursor.execute("select * from gasin")
            se = mycursor.fetchall()
            print("...........................       THE STORED DATA IS    .............................")
            print("                                                                                                                                                                                                 ")
            print("                                                                                                                                                                                                 ")
            print("                                                                                                                                                                                                 ")
            
            for x in se:
                print(x)
                print("____________________________________________________________________________________________________")

                continue
        elif choice==5:    
            customer_name=input("ENER yOUR NAME  : ")
            mycursor.execute("select  v_credit , v_debit ,v_accno , v_add from gasin where v_customer='customer_name'")
            record=mycursor.fetchall()
            for x in records:
                print(x)
            print(" continue your work")
            print("                                                                                                                                                                                                 ")
            print("                                                                                                                                                                                                 ")
            print("                                                                                                                                                                                                 ")

            continue
        elif choice==6:        
            v_customer=input("enter the name customer ")    
            v_accno=input("enter your acount number:")     
            import datetime
            v_date=datetime.datetime.now()
            date = v_date
            v_add=input("enter your complete address:")
            v_debit=input("enter your debit card number:")
            v_credit=int(input("enter your credit amount:"))
            mycursor.execute("insert into gasin values(v_customer,v_accno,'(date)', 'v_add',44453,1009900)")
            print("inserted")
        elif choice==0:
            break
        else:
            print ("<<<<<<  ...........IT IS INVALID CODE..........>>>>>>>>>>>")
            print("<<<<<<<...........Re-enter the suitable code........>>>>>>>>>>>")
            print("_______________________________________________________________________________")
            continue
else:
    print ("             SORRY!!! ......... THE PERSON IS UNIDETIFIED...........!!!        ")
    print ("        SORRY!!! ......... YOU ARE NOT SUPPOSE TO USE THE SOFTWARE......... !!!")
    quit
conn.commit()

