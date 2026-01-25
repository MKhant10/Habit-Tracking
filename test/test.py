import sqlite3
from datetime import datetime, timedelta

import pytest

from analysis.analysis import Analysis
from db.db import create_tables
from models.habits import Habit
from models.habit_manager import HabitManager

DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


def format_dt(dt_value):
    return dt_value.strftime(DATETIME_FMT)


def make_db():
    con = sqlite3.connect(":memory:")
    create_tables(con.cursor())
    return con


def insert_habit(
    con,
    habit_name,
    periodicity="daily",
    created_at=None,
    updated_at=None,
    streak_count=0,
):
    if created_at is None:
        created_at = datetime.now()
    if updated_at is None:
        updated_at = created_at
    cur = con.cursor()
    cur.execute(
        """
                INSERT INTO habit (HABIT_NAME, PERIODICITY, CREATEDDATE, UPDATEDDATE, STREAK_COUNT)
        VALUES (?, ?, ?, ?, ?);
                """,
        (
            habit_name,
            periodicity,
            format_dt(created_at),
            format_dt(updated_at),
            streak_count,
        ),
    )
    con.commit()
    return cur.lastrowid


def insert_completion(con, habit_id, completed_at):
    con.execute(
        """
                INSERT INTO completion (HABIT_ID, COMPLETED_AT) VALUES (?, ?);
                """,
        (habit_id, format_dt(completed_at)),
    )
    con.commit()


def set_inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda *args: next(iterator))


@pytest.fixture()
def db():
    con = make_db()
    yield con
    con.close()


@pytest.fixture()
def habit(db):
    return Habit(db=db)


@pytest.fixture()
def manager(db):
    return HabitManager(db=db)


@pytest.fixture()
def analysis(db):
    return Analysis(db=db)


def test_check_off(habit, db, monkeypatch, capsys):
    insert_habit(db, "walk", periodicity="daily", streak_count=0)
    set_inputs(monkeypatch, ["walk"])
    habit.check_off()
    output = capsys.readouterr().out
    row = db.execute(
        "SELECT STREAK_COUNT FROM habit WHERE HABIT_NAME=?;", ("walk",)
    ).fetchone()
    assert row[0] == 1
    assert "Checked off habit 'walk' successfully." in output


def test_refresh_all_habits(habit, db, capsys):
    habit_id = insert_habit(db, "walk", periodicity="daily", streak_count=2)
    now = datetime.now()
    day1 = now - timedelta(days=3)
    day2 = now - timedelta(days=2)
    insert_completion(db, habit_id, day1)
    insert_completion(db, habit_id, day2)
    habit.refresh_all_habits()
    output = capsys.readouterr().out
    row = db.execute(
        "SELECT STREAK_COUNT FROM habit WHERE HABIT_NAME=?;", ("walk",)
    ).fetchone()
    assert row[0] == 0
    assert "Database Refresh" in output


def test_add_habit_insert_row(manager, db, monkeypatch, capsys):
    set_inputs(monkeypatch, ["Walk", "daily"])
    manager.add_habit()
    output = capsys.readouterr().out
    row = db.execute(
        "SELECT HABIT_NAME, PERIODICITY FROM habit WHERE HABIT_NAME = ?;", ("walk",)
    ).fetchone()
    assert row is not None
    assert row[1] == "daily"
    assert "Habit 'walk' added successfully." in output


def test_update_habit_edit_row(manager, db, monkeypatch, capsys):
    insert_habit(db, "walk", periodicity="daily")
    set_inputs(monkeypatch, ["Walk", "Run", "weekly"])
    manager.update_habit()
    output = capsys.readouterr().out
    row = db.execute("SELECT HABIT_NAME FROM habit;").fetchone()
    assert row[0] == "Run"
    assert (
        "Habit name updated from 'walk' to 'Run' and periodicity is set to weekly."
        in output
    )


def test_delete_habit(manager, db, monkeypatch, capsys):
    insert_habit(db, "walk", periodicity="daily")
    set_inputs(monkeypatch, ["walk"])
    manager.delete_habit()
    output = capsys.readouterr().out
    row = db.execute(
        "SELECT HABIT_NAME FROM habit WHERE HABIT_NAME = ?;", ("walk",)
    ).fetchone()
    assert row is None
    assert "Habit 'walk' is deleted successfully." in output


def test_get_habit(manager, db, monkeypatch, capsys):
    insert_habit(db, "walk", periodicity="daily")
    set_inputs(monkeypatch, ["walk"])
    manager.get_habit()
    output = capsys.readouterr().out
    row = db.execute(
        "SELECT HABIT_NAME FROM habit WHERE HABIT_NAME = ?;", ("walk",)
    ).fetchone()
    assert row[0] == "walk"
    assert "Habit found: Walk | Periodicity: daily |" in output


def test_list_habits(manager, db, capsys):
    insert_habit(db, "walk", periodicity="daily")
    insert_habit(db, "read", periodicity="weekly")
    manager.list_habits()
    output = capsys.readouterr().out
    assert "walk (daily)" in output
    assert "read (weekly)" in output


def test_delete_all_habits(manager, db, monkeypatch, capsys):
    insert_habit(db, "walk", periodicity="daily")
    insert_habit(db, "read", periodicity="weekly")
    set_inputs(monkeypatch, ["yes"])
    manager.delete_all_habits()
    output = capsys.readouterr().out
    row = db.execute("SELECT * FROM habit;").fetchall()
    assert row == []
    assert "All habits have been deleted." in output


# Analysis tests:
# Longest streak overall
def test_longest_streak_overall_by_weekly(analysis, db, capsys):
    weekly_id = insert_habit(db, "weekly-habit", periodicity="weekly")
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    insert_completion(db, weekly_id, week_start - timedelta(days=14))
    insert_completion(db, weekly_id, week_start - timedelta(days=7))
    insert_completion(db, weekly_id, week_start)
    analysis.longest_streak_overall()
    output = capsys.readouterr().out
    assert "weekly-habit" in output
    assert "3" in output


def test_longest_streak_by_habit_daily(analysis, db, monkeypatch, capsys):
    habit_id = insert_habit(db, "read", periodicity="daily")
    now = datetime.now()
    insert_completion(db, habit_id, now - timedelta(days=1))
    insert_completion(db, habit_id, now)
    set_inputs(monkeypatch, ["read"])
    analysis.longest_streak_by_habit()
    output = capsys.readouterr().out
    assert "Longest streak for Habit 'read': 2" in output


def test_list_by_periodicity_filters(analysis, db, monkeypatch, capsys):
    insert_habit(db, "walk", periodicity="daily")
    insert_habit(db, "read", periodicity="weekly")
    set_inputs(monkeypatch, ["daily"])
    analysis.list_by_periodicity()
    output = capsys.readouterr().out
    assert "walk" in output
    assert "read" not in output


def test_broken_habits_detects_gap(analysis, db, capsys):
    habit_id = insert_habit(db, "walk", periodicity="daily")
    now = datetime.now()
    insert_completion(db, habit_id, now - timedelta(days=3))
    insert_completion(db, habit_id, now - timedelta(days=1))
    analysis.broken_habits()
    output = capsys.readouterr().out
    assert "walk" in output
