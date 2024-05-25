import sqlite3

## Connect to slite
connection = sqlite3.connect('student.db')

## Create a cursor object to insert record, create table, retrieve
cursor = connection.cursor()

#3 create the table
table_info = """
Create table STUDENT(NAME VARCHAR(25), CLSS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT);

"""

cursor.execute(table_info)

## Insert Some more records

cursor.execute("""Insert Into STUDENT values("Aariz","Data Science","A",90)""")
cursor.execute("""Insert Into STUDENT values("Dhanush","Cloud Computing","S",100)""")
cursor.execute("""Insert Into STUDENT values("Basha","Game Developer","B",80)""")
cursor.execute("""Insert Into STUDENT values("Harshit","Full Stack","C",70)""")
cursor.execute("""Insert Into STUDENT values("Sharath","Cyber Security","A",90)""")

## Display all the records
print("The insrted records are")

data = cursor.execute("""Select * From STUDENT""")

for row in data:
    print(row)

## Close the connection

connection.commit()
connection.close()