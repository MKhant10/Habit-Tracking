# Habit-Tracking Application
## Overview
A simple Python-based habit tracking application is designed and implemented that
helps users create and maintain consistent habits.


## Libraries and Version
Python Version -> 3.11.5

sqlite3 -> 3.51.0

pytest -> 9.0.2

fire -> 0.7.1


## Setup, Installation and Run
1. Clone the repository
```bash
git clone https://github.com/MKhant10/Habit-Tracking.git

cd Habit-Tracking
```
2. Setup virtual environment
```bash
python3 -m venv .venv
```
3. Activate the virtual environment
```bash
source .vene/bin/activate # MacOS
.venv\Scripts\activate.bat # Window Command Prompt
.venv\Scripts\Activate.ps1 # Window PowerShell
```
4. Install require libraries
```bash
pip install -r requirements.txt
```
5. Run the application
```bash
python main.py run
```
6. Deactivate the virtual environment
```bash
deactivate
```

## Basic Command Line Interface

Add a new habit by periodicity
```bash
python main.py add_habit
```
Update habit name and periodicity
```bash
python main.py update_habit
```
Delete existing habit
```bash
python main.py delete_habit
```
Get all information of an existing habit
```bash
python main.py get_habit
```
List all the existing habit
```bash
python main.py list_habit
```
Check off habit as completed in current period
```bash
python main.py check_off
```
Summary of Longest streak overall, Habits that have been completed in current period and Broken Habits
```bash
python main.py summary
```

## Test
To run the test
```bash
pytest test/test.py
```