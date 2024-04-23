import sqlite3
import pytest
from datetime import datetime, timedelta
from habit import Habit


def setup_function():
    # Create an SQLite DB connection and drop tables
    with sqlite3.connect(Habit._DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tracking")
        cursor.execute("DROP TABLE IF EXISTS habit")
        conn.commit()


def test_habit_creation_and_retrieval():
    # Create a habit and marks completions
    habit = Habit(habit_id=1, name="Exercise", description="Run for 30 minutes", periodicity="Daily")
    habit.save()

    for i in range(3):
        habit.mark_completed(datetime.today().date() - timedelta(days=i))

        # Assertions
        assert habit.name == "Exercise"
        assert habit.description == "Run for 30 minutes"
        assert habit.periodicity == "Daily"
        assert habit.calculate_current_daily_streak(habit_id=1) == 3





