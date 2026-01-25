from helper.common import *
from datetime import datetime

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
            raise ValueError(f"Habit '{habit_name}' does not exist.")

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