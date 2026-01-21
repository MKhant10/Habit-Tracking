import sys
from unittest import case
from models import HabitManager, Habit
import sqlite3
from db import create_tables
from analysis import Analysis

if __name__ == "__main__":
    file_path = "habit.db"
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    check_create_tables = create_tables(cur)
    if check_create_tables:
        print("Database and tables are ready.")
        manager = HabitManager(db=con)
        habit = Habit(db=con)
        analysis = Analysis(db=con)
        manager.seed()
        con.commit()
    habits = con.execute("SELECT HABIT_NAME, PERIODICITY FROM habit WHERE ONGOING = 1;")
    ongoing_habits = [f"{habit[0]} ({habit[1]})" for habit in habits.fetchall()]
    initial = True
    while initial:
        print(f"""
              Welcome to Habit Tracker.
              Ongoing Habits:
              {ongoing_habits if ongoing_habits else 'No ongoing habits found.'}
                """)
        print("\nMenu:")
        print("  1) Check-off Habit")
        print("  2) Habit Management")
        print("  3) Habit Analytics")
        print("  4) Exit")

        try:
            choice = input("\nSelect (1-4): ").strip()
            match choice:
                case "1":
                    habit.check_off()
                case "2":
                    print("Choose one of the following options below: ")
                    print("  1) Create Habit")
                    print("  2) Update Habit Name")
                    print("  3) Delete Existing Habit")
                    print("  4) Get Existing Habit")
                    print("  5) Show Existing Habits")
                    print("  6) Delete All Habits")
                    print("  7) Back to Main Menu")

                    while True:
                        habit_menu_choice = input("\nSelect (1-7): ").strip()

                        match habit_menu_choice:
                            case "1":
                                manager.add_habit()
                            case "2":
                                manager.update_habit_name()
                            case "3":
                                manager.delete_habit()
                            case "4":
                                manager.get_habit()
                            case "5":
                                manager.list_habits()
                            case "6":
                                manager.delete_all_habits()
                            case "7":
                                print("Going back to main menu.")
                                break
                            case _:
                                print("Invalid choice. Please select a valid option.")
                        
                case "3":
                    print("\nAnalytics Options: ")
                    print(" 1) Longest Streak Overall")
                    print(" 2) Longest Streak by Habit")
                    print(" 3) List Habits by Periodicity")
                    print(" 4) Broken Habits")
                    print(" 5) Back to Main Menu")
                    
                    while True:
                        analytics_menu_choice = input("\nSelect (1-5): ").strip()
                        
                        match analytics_menu_choice:
                            case "1":
                                analysis.longest_streak_overall()
                            case "2":
                                pass
                            case "3":
                                analysis.list_by_periodicity()
                            case "4":
                                analysis.broken_habits()
                            case "5":
                                print("Going back to main menu.")
                                break
                            case _:
                                print("Invalid choice. Please select a valid option.")
                                
                case "4":
                    con.close()
                    print("Exiting... Bye 👋")
                    sys.exit(0)
        except KeyboardInterrupt:
            con.close()
            print("\nBye 👋")
            initial = False

                

