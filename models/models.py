from datetime import datetime
import json
from helper.common import *
import os
from pathlib import Path


class Habit:
    """
    Habit Manager Class

    params:
        db: sqlite db connection
    """

    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    def check_off(self):
        habit_name = input("Enter Habit Name to check off: ").strip().lower()
        if check_habit_exist(self.cursor, habit_name):
            habit = self.cursor.execute(
                "SELECT HABIT_ID, PERIODICITY FROM habit WHERE LOWER(HABIT_NAME) = LOWER(?);",
                (habit_name,),
            ).fetchone()
            habit_id, periodicity = habit[0], habit[1]
            now = datetime.now()
            period_start = get_period_start(now, periodicity)
            period_end = get_period_end(period_start, periodicity)

            already_completed = self.cursor.execute(
                """SELECT 1 FROM completion
                WHERE HABIT_ID = ? AND COMPLETED_AT >= ? AND COMPLETED_AT < ? LIMIT 1;""",
                (habit_id, period_start, period_end),
            ).fetchone()

            if already_completed:
                print(
                    f"{habit_name} has already been checked off for the current {periodicity} period."
                )
                return
            self.cursor.execute(
                """
                                INSERT INTO completion (HABIT_ID, COMPLETED_AT)
                                VALUES (?, ?);""",
                (habit_id, now),
            )

            self.cursor.execute(
                """
                                UPDATE habit SET STREAK_COUNT = STREAK_COUNT + 1 , UPDATEDDATE = ?
                                WHERE HABIT_ID = ?;""",
                (now, habit_id),
            )

            self.db.commit()
            print(f"\nChecked off habit '{habit_name}' successfully.")
        else:
            print(f"Habit '{habit_name}' does not exist.")

    def _refresh_streak_if_broken(self, habit_id, now):
        if now is None:
            now = datetime.now()

        query = """SELECT PERIODICITY, STREAK_COUNT FROM habit WHERE HABIT_ID = ?;"""
        row = self.cursor.execute(query, (habit_id,)).fetchone()
        if not row:
            return False
        periodicity = row[0]
        last_completion = self.cursor.execute(
            """
                                              SELECT MAX(COMPLETED_AT) FROM completion WHERE HABIT_ID = ?
                                              """,
            (habit_id,),
        ).fetchone()
        last_complete = last_completion[0]
        if not last_complete:
            return False
        last_complete = parse_datetime(last_complete)

        last_period_start = get_period_start(last_complete, periodicity)
        next_period_start = get_period_end(last_period_start, periodicity)
        current_period_start = get_period_start(now, periodicity)
        # print(last_period_start,current_period_start, next_period_start)

        if current_period_start > next_period_start:
            self.cursor.execute(
                """
                                UPDATE habit SET STREAK_COUNT = 0, UPDATEDDATE = ? WHERE HABIT_ID = ?;""",
                (
                    now,
                    habit_id,
                ),
            )
            self.db.commit()
            return True
        return False

    def refresh_all_habits(self):
        habit_ids = self.cursor.execute("""SELECT HABIT_ID FROM habit;""").fetchall()
        for habit_id in habit_ids:
            self._refresh_streak_if_broken(habit_id[0], None)
        print("\nDatabase Refresh")

    def __repr__(self):
        return f"Habit(name={self.name}, periodicity={self.periodicity})"


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
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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


# import sqlite3
# con = sqlite3.connect("habit.db")
# cur = con.cursor()
# query = "SELECT HABIT_ID FROM habit;"
# rows = cur.execute(query).fetchall()
# for row in rows:
#     habit_ids = row[0]
#     Habit(con)._refresh_streak_if_broken(habit_ids, None)
