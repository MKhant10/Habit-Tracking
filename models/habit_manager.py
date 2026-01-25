from datetime import datetime
import json
from helper.common import *
import os
from pathlib import Path

class HabitManager:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    def seed(self):
        existing = self.cursor.execute("SELECT COUNT(1) FROM habit;").fetchone()[0]
        if existing > 0:
            print("\nSeed skipped: data already exist.")
            return
        path = Path("db/habits.json")
        if not os.path.exists(path):
            print("No seed file found.")
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        habits = data.get("habits", [])
        completions = data.get("completion", [])
        if not isinstance(habits, list) or not habits:
            return "Empty habits to seed."
        query = """
        INSERT INTO habit (HABIT_NAME, PERIODICITY, STREAK_COUNT)
        VALUES (?, ?, ?);"""
        for habit in habits:
            habit_name = habit["habit_name"].strip().lower()
            if not check_habit_exist(self.cursor, habit_name):
                self.cursor.execute(
                    query, (habit_name, habit["periodicity"], habit["streak_count"])
                )
                self.db.commit()

        query_completion = """
        INSERT INTO completion (HABIT_ID, COMPLETED_AT)
        VALUES (?, ?);"""
        for completion in completions:
            habit_id = completion["habit_id"].strip()
            self.cursor.execute(
                query_completion, (habit_id, completion["completed_at"])
            )
            self.db.commit()
        print(f"\nSeeded {len(habits)} habits successfully.")

    def add_habit(self):
        habit_data = dict()

        habit_data["name"] = input("Enter Habit Name: ").strip().lower()

        periodicity = input("Enter Periodicity (daily/weekly): ").strip().lower()
        while periodicity not in ["daily", "weekly"]:
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
            periodicity = input("Enter Periodicity (daily/weekly): ").strip().lower()
        habit_data["periodicity"] = periodicity

        query = """
        INSERT INTO habit (HABIT_NAME, PERIODICITY,STREAK_COUNT)
        VALUES (?,?, 0)"""
        try:
            self.cursor.execute(query, (habit_data["name"], habit_data["periodicity"]))
            self.db.commit()
            print(f"\nHabit '{habit_data['name']}' added successfully.")
        except Exception as e:
            print(f"Error adding habit to database: {e}")

    def update_habit(self):
        display_habits(self.db)
        habit_name = input("Enter the name of the habit to update: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            new_name = input("Enter the new name for the habit: ").strip()
            updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            periodicity = input("Enter Periodicity (daily/weekly): ").strip().lower()
            while periodicity not in ["daily", "weekly"]:
                print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
                periodicity = (
                    input("Enter Periodicity (daily/weekly): ").strip().lower()
                )
            query = """
            UPDATE habit SET HABIT_NAME = ? ,PERIODICITY = ?, UPDATEDDATE = ? WHERE HABIT_NAME = ?;"""
            self.cursor.execute(
                query, (new_name, periodicity, updated_date, habit_name)
            )
            self.db.commit()
            print(
                f"\nHabit name updated from '{habit_name}' to '{new_name}' and periodicity is set to {periodicity}."
            )
        else:
            print(f"Habit '{habit_name}' does not exist.")

    def delete_habit(self):
        display_habits(self.db)
        habit_name = input("Enter Habit Name to delete: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            query = """
            DELETE FROM habit WHERE HABIT_NAME = ?;"""
            self.cursor.execute(query, (habit_name,))
            self.db.commit()
            print(f"\nHabit '{habit_name}' is deleted successfully.")
        else:
            print(f"Habit '{habit_name}' does not exist.")

    def get_habit(self):
        display_habits(self.db)
        habit_name = input("Enter Habit Name to search: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            query = """
            SELECT * FROM habit WHERE HABIT_NAME = ?;"""
            habit = self.cursor.execute(query, (habit_name,)).fetchone()
            print(
                f"\nHabit found: {habit[1].capitalize()} | Periodicity: {habit[2]} | Created Date: {habit[3]} | Updated Date: {habit[4]} | Streak Count: {habit[5]}"
            )
        else:
            print(f"Habit '{habit_name}' does not exist.")

    def list_habits(self):
        habits = self.cursor.execute(
            """SELECT HABIT_NAME, PERIODICITY FROM habit"""
        ).fetchall()
        print(f"\nExisting Habits: ")
        for idx, habit in enumerate(habits, start=1):
            print(f"{idx}. {habit[0]} ({habit[1]})")

    def delete_all_habits(self):
        confirm = (
            input("Are you sure you want to delete all habits? (yes/no): ")
            .strip()
            .lower()
        )
        if confirm == "yes":
            query = """DELETE FROM habit;"""
            self.cursor.execute(query)
            self.db.commit()
            print("All habits have been deleted.")
        else:
            print("Operation cancelled.")