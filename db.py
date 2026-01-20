# import the sqlite3 package


# create a database named habit.db

def create_tables(cur):
    # create a table named habit
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS habit(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    HABIT_NAME TEXT,
    PERIODICITY TEXT,
    CREATEDDATE DATE,
    ONGOING BOOLEAN,
    STREAK_COUNT INTEGER,
    UPDATEDDATE DATE);''')

    cur.execute(
    '''CREATE TABLE IF NOT EXISTS completion(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    HABIT_ID INTEGER,
    HABIT_NAME TEXT,
    COMPLETED_AT DATE,
    FOREIGN KEY (HABIT_NAME) REFERENCES habit(HABIT_NAME),
    FOREIGN KEY (HABIT_ID) REFERENCES habit(ID));''')
    return True

