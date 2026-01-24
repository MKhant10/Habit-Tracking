from datetime import datetime
from helper.common import *

class Analysis:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    # Get completed habits in the current period
    def _completed_habits(self, habit_id, periodicity, now):
        start_date = get_period_start(now, periodicity)
        end_date = get_period_end(start_date, periodicity)

        completions = self.cursor.execute(
            """SELECT 1 FROM completion
        WHERE HABIT_ID = ? AND COMPLETED_AT >= ? AND COMPLETED_AT < ? LIMIT 1;
        """,
            (habit_id, start_date, end_date),
        ).fetchone()
        return completions is not None

    # Get all unique completions periods for a habit based on periodicity
    def _get_completion_periods(self, habit_id, periodicity):
        step = period_step(periodicity)
        if step is None:
            return []
        query = """ SELECT COMPLETED_AT FROM completion WHERE HABIT_ID = ?;"""
        rows = self.cursor.execute(query, (habit_id,)).fetchall()
        periods = set()
        for row in rows:
            dt_value = parse_datetime(row[0])
            if not dt_value:
                continue
            start_date = get_period_start(dt_value, periodicity)
            if start_date is not None:
                periods.add(start_date)
        return sorted(periods)

    # Calculate the longest streak from a list of period starts
    def _longest_streak_from_periods(self, period_starts, periodicity):
        step = period_step(periodicity)
        if not period_starts or step is None:
            return 0
        longest = 1
        current = 1
        prev = period_starts[0]
        for period_start in period_starts[1:]:
            if period_start - prev == step:
                current += 1
            else:
                current = 1
            if current > longest:
                longest = current
            prev = period_start
        return longest

    # Check if there is a gap in the streak
    def _has_streak_gap(self, period_starts, periodicity):
        step = period_step(periodicity)
        if step is None or len(period_starts) <= 1:
            return False
        prev = period_starts[0]
        for period_start in period_starts[1:]:
            if period_start - prev > step:
                return True
            prev = period_start
        return False

    # Determine if a habit is broken based on its periodicity and completion history=
    def _is_broken(self, periodicity, created_at, period_starts):
        step = period_step(periodicity)
        if step is None:
            return False
        current_period = get_period_start(datetime.now(), periodicity)
        if not period_starts:
            created_dt = parse_datetime(created_at)
            if not created_dt:
                return False
            created_period = get_period_start(created_dt, periodicity)
            return (current_period - created_period) >= step
        if self._has_streak_gap(period_starts, periodicity):
            return True
        return (current_period - period_starts[-1]) > step

    # Calculate longest streak overall
    def longest_streak_overall(self):
        query = """
        SELECT HABIT_ID, HABIT_NAME, PERIODICITY FROM habit;"""
        habits = self.cursor.execute(query).fetchall()
        if not habits:
            print("No habits found.")
            return
        best_streak = 0
        best_habits = []
        for habit_id, habit_name, periodicity in habits:
            periodicity = (periodicity or "").strip().lower()
            period_starts = self._get_completion_periods(habit_id, periodicity)
            streak = self._longest_streak_from_periods(period_starts, periodicity)
            if streak > best_streak:
                best_streak = streak
                best_habits = [(habit_name, periodicity)]
            elif streak == best_streak and streak > 0:
                best_habits.append((habit_name, periodicity))
            if best_streak == 0:
                print("No completions found yet")
                return
            if len(best_habits) == 1:
                habit_name, periodicity = best_habits[0]
                print(
                    f"Longest streak overall: Habit '{habit_name}' with a streak of {best_streak}"
                )
                return
            print(f"Longest streak overall: {best_streak} periods.")
            for habit_name, periodicity in best_habits:
                print(f"- {habit_name} ({periodicity})")

    # Calculate longest streak by Habit
    def longest_streak_by_habit(self):
        habit_name = input("Enter Habit Name to check longest streak: ").strip().lower()
        if not habit_name:
            print("Habit name is required.")
            return
        query = """
        SELECT HABIT_ID, HABIT_NAME, PERIODICITY FROM habit WHERE HABIT_NAME = ? COLLATE NOCASE;"""
        habit = self.cursor.execute(query, (habit_name,)).fetchone()
        if not habit:
            print(f"Habit {habit_name} does not exist.")
            return
        habit_id, habit_name, periodicity = habit
        periodicity = (periodicity or "").strip().lower()
        period_starts = self._get_completion_periods(habit_id, periodicity)
        streak = self._longest_streak_from_periods(period_starts, periodicity)
        if streak == 0:
            print(f"Habit '{habit_name}' has no completions yet.")
            return
        print(f"Longest streak for Habit '{habit_name}': {streak}.")

    # List by periodicity
    def list_by_periodicity(self):
        periodicity = input("Enter periodicity (daily/weekly): ").strip().lower()
        while periodicity not in ["daily", "weekly"]:
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
            periodicity = input("Enter periodicity (daily/weekly): ").strip().lower()

        query = """
        SELECT HABIT_NAME FROM habit WHERE PERIODICITY = ?;"""
        habits = self.cursor.execute(query, (periodicity,)).fetchall()
        print(f"Habits to do in {periodicity}: ")
        for habit in habits:
            print(f"- {habit[0]}")

    # Identify Broken Habits
    def broken_habits(self):
        query = """
        SELECT HABIT_ID, HABIT_NAME, PERIODICITY, CREATEDDATE FROM habit;"""
        habits = self.cursor.execute(query).fetchall()
        if not habits:
            print("No habits found.")
            return
        broken = []
        for habit_id, habit_name, periodicity, created_at in habits:
            periodicity = (periodicity or "").strip().lower()
            period_starts = self._get_completion_periods(habit_id, periodicity)
            if self._is_broken(periodicity, created_at, period_starts):
                broken.append(habit_name)
        if not broken:
            print("No broken habits found.")
            return
        print("Broken Habits: ")
        for habit_name in broken:
            print(f"- {habit_name}")

    def list_incompleted_habits(self):
        now = datetime.now()
        habits = self.db.execute(
            "SELECT HABIT_ID, HABIT_NAME, PERIODICITY FROM habit;"
        ).fetchall()

        if not habits:
            print("No habits found.")
            return
        print("\nHabits needs to be done in current period:")
        for habit_id, habit_name, periodicity in habits:
            completed = self._completed_habits(habit_id, periodicity, now)
            if not completed:
                print(f"- {habit_name} ({periodicity})")
        if completed:
            print("No incompleted Habits")

    def list_completed_habits(self):
        now = datetime.now()
        habits = self.db.execute(
            "SELECT HABIT_ID, HABIT_NAME, PERIODICITY FROM habit;"
        ).fetchall()

        if not habits:
            print("No habits found.")
            return
        print("\nHabits needs to be done in current period:")
        for habit_id, habit_name, periodicity in habits:
            completed = self._completed_habits(habit_id, periodicity, now)
            if completed:
                print(f"- {habit_name} ({periodicity})")
