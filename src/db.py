# import the sqlite3 package
import sqlite3  

# create a database named habit.db
cnt = sqlite3.connect("habit.db")  

# create a table named habit
cnt.execute('''CREATE TABLE habit(
ID INTEGER PRIMARY KEY AUTOINCREMENT,
NAME TEXT,
PERIODICITY TEXT,
CREATEDDATE DATE,
ONGOING BOOLEAN,
STREAK_COUNT INTEGER);''')

cnt = execute('''
              CREATE TABLE completion(
                  ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  HABIT_ID INTEGER FOREIGN KEY REFERENCES habit(ID),
                  COMPLETED_AT DATE);''')