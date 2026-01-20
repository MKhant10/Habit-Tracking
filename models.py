from datetime import datetime
import json
from common import check_habit_exist
import os
from pathlib import Path

class Habit():
    # def __init__(self, db):
    #     self.db = db
    
    # def check_off(self):
    #     habit_name = input("Enter Habit Name to check off: ").strip()
    #     query = """
    #     UPDATE habit SET STREAK_COUNT = STREAK_COUNT + 1, UPDATEDDATE = ? WHERE NAME = ?;"""
    #     all_habits = self.db.execute("SELECT NAME FROM habit;").fetchall()
    #     if check_habit_exist(all_habits, habit_name):
    #         updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #         self.db.execute(query, (updated_date, habit_name))
    #         print(f"Habit '{habit_name}' checked off successfully.")
    #     else:
    #         print(f"Habit '{habit_name}' does not exist.")
            
            
    def completion_dates():
        pass
    
    def is_due(self):
        pass
    
    def __repr__(self):
        return f"Habit(name={self.name}, periodicity={self.periodicity})"
    
class HabitManager():
    def __init__(self, db):
        # self.habits = []
        self.db = db
        self.cursor = db.cursor()
        
    def seed(self):
        path = Path("habits.json")
        if not os.path.exists(path):
            print("No seed file found.")
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        habits = data.get("habits", [])
        if not isinstance(habits, list) or not habits:
            return "Empty habits to seed."
        query = """
        INSERT INTO habit (HABIT_NAME, PERIODICITY, ONGOING, STREAK_COUNT, CREATEDDATE, UPDATEDDATE)
        VALUES (?, ?, ?, ?, ?, ?)"""
        date = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")
        for habit in habits:
            habit_name = habit['habit_name'].strip().lower()
            if not check_habit_exist(self.cursor, habit_name):
                self.cursor.execute(query, (
                    habit_name,
                    habit['periodicity'],
                    habit['ongoing'],
                    habit['streak'],
                    date, date
                    ))
                self.db.commit()
        print(f"Seeded {len(habits)} habits successfully.")
        
    def add_habit(self):
        habit_data = dict()
        
        habit_data['name'] = input("Enter Habit Name: ").strip().lower()
        
        periodicity = (
            input("Enter Periodicity (daily/weekly): ").strip().lower()
            )
        while periodicity not in ['daily', 'weekly']:
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
            periodicity = (input("Enter Periodicity (daily/weekly): ").strip().lower())
        habit_data['periodicity'] = periodicity
        
        habit_data['createdDate'] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")
        habit_data['updatedDate'] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")
        habit_data['ongoing'] = True
        habit_data['streak_count'] = 0
        
        query = """
        INSERT INTO habit (HABIT_NAME, PERIODICITY, CREATEDDATE, UPDATEDDATE, ONGOING, STREAK_COUNT)
        VALUES (?, ?, ?, ?, ?, ?)"""
        try:
            self.cursor.execute(query, (
            habit_data['name'],
            habit_data['periodicity'],
            habit_data['createdDate'],
            habit_data['updatedDate'],
            habit_data['ongoing'],
            habit_data['streak_count']
            ))
            self.db.commit()
            print(f"Habit '{habit_data['name']}' added successfully.")    
        except Exception as e:
            print(f"Error adding habit to database: {e}")
    
    def update_habit_name(self):
        habit_name = input("Enter the name of the habit to update: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            new_name = input("Enter the new name for the habit: ").strip()
            updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
            UPDATE habit SET HABIT_NAME = ? , UPDATEDDATE = ? WHERE HABIT_NAME = ?;"""
            self.cursor.execute(query, (new_name, updated_date, habit_name))
            self.db.commit()
            print(f"Habit name updated from '{habit_name}' to '{new_name}'.")
        else:
            print(f"Habit '{habit_name}' does not exist.")
    
    
    def delete_habit(self):
        habit_name = input("Enter Habit Name to delete: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            query = """
            DELETE FROM habit WHERE HABIT_NAME = ?;"""
            self.cursor.execute(query, (habit_name,))
            self.db.commit()
            print(f"Habit '{habit_name}' removed successfully.")
        else:
            print(f"Habit '{habit_name}' does not exist.")
            
    def get_habit(self):
        habit_name = input("Enter Habit Name to search: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            query = """
            SELECT * FROM habit WHERE HABIT_NAME = ?;"""
            habit = self.cursor.execute(query, (habit_name,)).fetchone()
            print(f"Habit found: {habit[1].capitalize()} | Periodicity: {habit[2]} | Created Date: {habit[3]} | Ongoing: {habit[4]} | Streak Count: {habit[5]} | Updated Date: {habit[6]}")
        else:
            print(f"Habit '{habit_name}' does not exist.")

    def list_habits(self):
        res = self.cursor.execute("""SELECT HABIT_NAME, PERIODICITY FROM habit""")
        habits = res.fetchall()
        print(f"Existing Habits: ")
        for idx, habit in enumerate(habits, start=1):
            print(f" {idx}. {habit[0]} ({habit[1]})")
    
    def delete_all_habits(self):
        confirm = input("Are you sure you want to delete all habits? (yes/no): ").strip().lower()
        if confirm == 'yes':
            query = """DELETE FROM habit;"""
            self.cursor.execute(query)
            self.db.commit()
            print("All habits have been deleted.")
        else:
            print("Operation cancelled.")
            
    def check_off(self):
        habit_name = input("Enter Habit Name to check off: ").strip().lower()
        query_1 = """
        UPDATE habit SET STREAK_COUNT = STREAK_COUNT + 1, UPDATEDDATE = ? WHERE HABIT_NAME = ?;
        """
        query_2 = """
        INSERT INTO completion (HABIT_ID, COMPLETED_AT) VALUES ((SELECT ID FROM habit WHERE HABIT_NAME = ?), ?);
        """
        if check_habit_exist(self.cursor, habit_name):
            updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(query_1, (updated_date, habit_name))
            self.cursor.execute(query_2, (habit_name, updated_date))
            self.db.commit()
            print(f"Habit '{habit_name}' checked off successfully.")
        else:
            print(f"Habit '{habit_name}' does not exist.")
            
