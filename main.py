import atexit
from models.models import HabitManager, Habit
import sqlite3
from db.db import create_tables
from analysis.analysis import Analysis
import fire


class HabitCLI:
    def __init__(self, db_path="db/habit.db", seed=True):
        self.db_path = db_path
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        create_tables(self.cur)

        self.manager = HabitManager(db=self.con)
        self.habit = Habit(db=self.con)
        self.analysis = Analysis(db=self.con)

        if seed:
            self.manager.seed()
            self.con.commit()
        atexit.register(self.close)

    def close(self):
        if self.con:
            self.con.close()
            self.con = None

    def add_habit(self):
        self.manager.add_habit()

    def update_habit(self):
        self.manager.update_habit()

    def delete_habit(self):
        self.manager.delete_habit()

    def get_habit(self):
        self.manager.get_habit()

    def list_habit(self):
        self.manager.list_habits()

    def run(self):
        initiate = True
        while initiate:
            self.habit.refresh_all_habits()
            self.analysis.list_incompleted_habits()
            print("\nMenu:")
            print("  1) Check-off Habit")
            print("  2) Habit Management")
            print("  3) Habit Analytics")
            print("  4) Exit")

            try:
                choice = input("\nSelect (1-4): ").strip()
                match choice:
                    case "1":
                        self.habit.check_off()
                    case "2":

                        while True:
                            print("\nChoose one of the following options below: ")
                            print("  1) Create Habit")
                            print("  2) Update Habit Name")
                            print("  3) Delete Existing Habit")
                            print("  4) Get Existing Habit")
                            print("  5) Show Existing Habits")
                            print("  6) Delete All Habits")
                            print("  7) Back to Main Menu")
                            habit_menu_choice = input("\nSelect (1-7): ").strip()

                            match habit_menu_choice:
                                case "1":
                                    self.manager.add_habit()
                                case "2":
                                    self.manager.update_habit_name()
                                case "3":
                                    self.manager.delete_habit()
                                case "4":
                                    self.manager.get_habit()
                                case "5":
                                    self.manager.list_habits()
                                case "6":
                                    self.manager.delete_all_habits()
                                case "7":
                                    print("Going back to main menu.")
                                    break
                                case _:
                                    print(
                                        "Invalid choice. Please select a valid option."
                                    )

                    case "3":
                        while True:
                            print("\nAnalytics Options: ")
                            print(" 1) Longest Streak Overall")
                            print(" 2) Longest Streak by Habit")
                            print(" 3) List Habits by Periodicity")
                            print(" 4) Broken Habits")
                            print(" 5) Back to Main Menu")
                            analytics_menu_choice = input("\nSelect (1-5): ").strip()

                            match analytics_menu_choice:
                                case "1":
                                    self.analysis.longest_streak_overall()
                                case "2":
                                    self.analysis.longest_streak_by_habit()
                                case "3":
                                    self.analysis.list_by_periodicity()
                                case "4":
                                    self.analysis.broken_habits()
                                case "5":
                                    print("Going back to main menu.")
                                    break
                                case _:
                                    print(
                                        "Invalid choice. Please select a valid option."
                                    )

                    case "4":
                        self.close()
                        print("\nExiting... Bye 👋")
                        print()
                        initiate = False
            except KeyboardInterrupt:
                self.close()
                print("\nBye 👋")
                print()
                initiate = False


def main():
    fire.Fire(HabitCLI)


if __name__ == "__main__":
    main()
