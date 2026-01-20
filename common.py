def check_habit_exist(db, name):
    """checking the existing habits

    Args:
        db : connection
        name (str): habit name you want to check
    """
    # return any(habit for habit in habits if habit['name'].lower() == name.lower())
    habits = db.execute("SELECT HABIT_NAME FROM habit;").fetchall()
    return any(h[0].strip().lower() == name for h in habits)
