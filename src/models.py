from datetime import datetime

class Habit():
    def __init__(self, id, name, periodicity, createdDate, completions):
        self.id = id
        self.name = name
        self.periodicity = periodicity
        self.createdDate = createdDate
        self.completions = completions
        
    def check_off(self, name):
        pass
    
    def completion_dates():
        pass
    
    def is_due(self):
        pass
    
    def __repr__(self):
        return f"Habit(name={self.name}, periodicity={self.periodicity})"
    
class HabitManager():
    def __init__(self):
        self.habits = []
        
    def add_habit(self, habit):
        habit_data = dict()
        
        name = input("Enter Habit Name: ")
        habit_data['name'] = name
        
        periodicity = (
            input("Enter Periodicity (daily/weekly): ").lower()
            )
        while periodicity not in ['daily', 'weekly']:
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
            periodicity = (input("Enter Periodicity (daily/weekly): ").lower())
        habit_data['periodicity'] = periodicity
        
        habit_data['createdDate'] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")
        habit_data['updatedDate'] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")
        habit_data['ongoing'] = True
        habit_data['streak_count'] = 0
        self.habits.append(habit_data)
        print(f"Habit '{habit_data['name']}' added successfully.")
    
    def remove_habit(self, habit_id):
        pass
    
    def get_habit(self, habit_id):
        pass
    
    def list_habits(self):
        pass
    
    