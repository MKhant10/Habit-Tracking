from datetime import datetime, timedelta


def check_habit_exist(db, name):
    """checking the existing habits

    Args:
        db : connection
        name (str): habit name you want to check
    """
    # return any(habit for habit in habits if habit['name'].lower() == name.lower())
    habits = db.execute("SELECT HABIT_NAME FROM habit;").fetchall()
    return any(h[0].strip().lower() == name for h in habits)


def display_habits(db):
    habits = db.execute("""SELECT HABIT_NAME FROM habit""").fetchall()
    print("\nHabits to choose: ")
    for habit in habits:
        print(f"- {habit[0]}")


# Get period start and end dates based on periodicity
def get_period_start(dt_value, periodicity):
    date_value = dt_value.date()
    if periodicity == "daily":
        return date_value
    elif periodicity == "weekly":
        start_of_week = date_value - timedelta(days=date_value.weekday())
        return start_of_week
    else:
        raise ValueError("Invalid periodicity. Must be 'daily' or 'weekly'.")


def get_period_end(start_date, periodicity):
    if periodicity == "daily":
        end_day = start_date + timedelta(days=1)
        return end_day
    elif periodicity == "weekly":
        end_of_week = start_date + timedelta(days=(7))
        return end_of_week
    else:
        raise ValueError("Invalid periodicity. Must be 'daily' or 'weekly'.")


# Convert datetime string to a datetime object
def parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    if isinstance(value, str):
        for format in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f"):
            try:
                return datetime.strptime(value, format)
            except ValueError:
                continue
    return None


# Get the time delta for the given periodicity
def period_step(periodicity):
    if periodicity == "daily":
        return timedelta(days=1)
    elif periodicity == "weekly":
        return timedelta(days=7)
    else:
        raise ValueError("Invalid periodicity. Must be 'daily' or 'weekly'.")
