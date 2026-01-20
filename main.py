from unittest import case
from models import HabitManager
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
        analysis = Analysis(db=con)
        manager.seed()
        con.commit()
while True:
    print("\nMenu:")
    print("  1) Habit Management")
    print("  2) Habit Analytics")
    print("  3) Exit")

    choice = input("\nSelect (1-3): ").strip()

    try:
        match choice:
            case "1":
                print("Choose one of the following options below: ")
                print("  1) Create Habit")
                print("  2) Update Habit Name")
                print("  3) Delete Existing Habit")
                print("  4) Get Existing Habit")
                print("  5) Show Existing Habits")
                print("  6) Delete All Habits")
                print("  7) Check Off Habit")

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
                        manager.check_off()
                    case _:
                        print("Invalid choice. Please select a valid option.")
            case "2":
                print("\nAnalytics Options: ")
                print(" 1) Longest Streak Overall")
                print(" 2) Longest Streak by Habit")
                print(" 3) List Habits by Periodicity")
                print(" 4) Broken Habits")
                print(" 5) Back")
                print(" 6) Back to Main Menu")
                
                analytics_menu_choice = input("\nSelect (1-6): ").strip()
                
                match analytics_menu_choice:
                    case "1":
                        analysis.longest_streak_overall()
                    case "2":
                        pass
                    case "3":
                        analysis.list_by_periodicity()
                    case _:
                        print("Invalid choice. Please select a valid option.")
    except KeyboardInterrupt:
        con.close()
        print("\nBye 👋")
        
                
    
