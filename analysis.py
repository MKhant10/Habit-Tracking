from datetime import datetime
import json
from common import check_habit_exist
import os

class Analysis:
    def __init__(self, db):
            self.db = db
            self.cursor = db.cursor()
    
    def longest_streak_overall(self):
        query = """
        SELECT HABIT_NAME, MAX(STREAK_COUNT) FROM habit;"""
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        print(f"Longest Streak Overall: Habit '{result[0]}' with a streak of {result[1]} days.")
        
    def longest_streak_by_habit(self):
        habit_name = input("Enter Habit Name to check longest streak: ").strip()
        query = """
        SELECT HABIT_NAME, STREAK_COUNT FROM habit WHERE HABIT_NAME = ?;"""
        self.cursor.execute(query, (habit_name,))
        result = self.cursor.fetchone()
        if result:
            print(f"Longest Streak for Habit '{result[0]}': {result[1]} days.")
        else:
            print(f"Habit '{habit_name}' does not exist.")
        
    def list_by_periodicity(self):
        periodicity = input("Enter periodicity (daily/weekly): ").strip().lower()
        while periodicity not in ['daily', 'weekly']:
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
            periodicity = input("Enter periodicity (daily/weekly): ").strip().lower()

        query = """
        SELECT HABIT_NAME FROM habit WHERE PERIODICITY = ?;"""
        self.cursor.execute(query, (periodicity,))
        results = self.cursor.fetchall()
        print(results)
        print(f"Habits to do in {periodicity}: ")
        for row in results:
            print(f"- {row[0]}")