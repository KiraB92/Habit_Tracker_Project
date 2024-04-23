import sqlite3
from datetime import datetime, timedelta
import questionary


class Habit:

    _DB_NAME = "habits.db"

    def __init__(self, habit_id=None, name=None, description=None, periodicity=None):
        self.habit_id = habit_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self._initialize_db()
        self.completed_dates = []

    # Initialization of the database
    def _initialize_db(self):
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS habit (
                               id INTEGER PRIMARY KEY,
                               name TEXT NOT NULL,
                               description TEXT NOT NULL,
                               periodicity TEXT NOT NULL
                               )
                           """)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS tracking (
                           id INTEGER PRIMARY KEY,
                           habit_id INTEGER,
                           completed_date DATETIME,
                           FOREIGN KEY (habit_id) REFERENCES habit(id)
                           )
                       """)
            conn.commit()

    # All the functions that have to do with the basic creation of the habits
    # and their storage and retrieval from the database.

    def save(self):
        """ Saves the habit to the database"""
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            if self.habit_id:
                # Update existing habit metadata
                cursor.execute("""
                    UPDATE habit SET name = ?, description = ?, periodicity = ? WHERE id = ?
                """, (self.name, self.description, self.periodicity, self.habit_id))
            else:
                # Insert new habit metadata
                cursor.execute("""
                    INSERT INTO habit (name, description, periodicity) VALUES (?, ?, ?)
                """, (self.name, self.description, self.periodicity))
                self.habit_id = cursor.lastrowid

            # Get existing completions for this habit
            cursor.execute("""
                SELECT completed_date FROM tracking WHERE habit_id = ?
            """, (self.habit_id,))
            existing_dates = {row[0] for row in cursor.fetchall()}

            # Insert new completions that don´t already exist in the database
            for date in [d.isoformat() for d in self.completed_dates if d.isoformat() not in existing_dates]:
                cursor.execute("""
                    INSERT INTO tracking (habit_id, completed_date) VALUES (?, ?)
                """, (self.habit_id, date))

            conn.commit()

    def delete_habit(self):
        """Deletes a habit from the database"""
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            if self.habit_id:
                cursor.execute("""
                DELETE FROM habit WHERE id = ?
                """, (self.habit_id, ))

            else:
                return None

            conn.commit()

    @classmethod
    def get_by_id(cls, habit_id):
        """Retrieve a habit by its ID along with its tracking data."""
        with sqlite3.connect(cls._DB_NAME) as conn:
            cursor = conn.cursor()

            # Fetch habit metadata
            cursor.execute("""
                    SELECT id, name, description, periodicity FROM habit WHERE id = ?
                """, (habit_id,))
            result = cursor.fetchone()
            if not result:
                return None

            habit = cls(habit_id=result[0], name=result[1], description=result[2], periodicity=result[3])

            # Fetch habit completions
            cursor.execute("""
                    SELECT completed_date FROM tracking where habit_id = ?
                """, (habit_id,))
            habit.completed_dates = [datetime.fromisoformat(row[0]).date() for row in cursor.fetchall()]

            return habit

    def __str__(self):
        return (f"Habit ID: {self.habit_id}\nHabit: {self.name}\n" +
                f"Description: {self.description}\nPeriodicity: {self.periodicity}\n")

    # The following are the functions that deal with the analysis of the habit.

    def mark_completed(self, date=None):
        if date is None:
            date = datetime.now()
            if date not in self.completed_dates:
                self.completed_dates.append(date)

    # GETS ALL SAVED TRACKING DATA
    def get_tracking_data(self, habit_id):
        """
        Gets the date and time of completion of a specific habit from the tracking table of the database.

        Parameter
        ----------
        The parameter is assigned within the functions calculate_current_daily_streak,
        calculate_current_weekly_streak, calculate_longest_daily_streak or calculate_longest_weekly_streak.

        :param habit_id: int

        Returns
        -------
        :return:
        tracking data --> if there is any saved tracking data for a specific habit
        None --> if there is no saved tracking data for a specific habit
            """
        with (sqlite3.connect(self._DB_NAME) as conn):
            cursor = conn.cursor()
            cursor.execute("""
                SELECT completed_date FROM tracking WHERE habit_id = ?
            """, (self.habit_id, ))
            existing_dates = [row[0] for row in cursor.fetchall()]

            if len(existing_dates) > 0:
                return existing_dates

            else:
                return None

    # COMPUTES THE CURRENT STREAK OF A HABIT WITH THE PERIODICITY DAILY
    def calculate_current_daily_streak(self, habit_id):
        """
        Computes the current streak of a habit with the periodicity daily.

        Function cannot be called directly by the user but is used within other functions.

        Parameters
        ----------
        :param habit_id: the habit id
            Is assigned by the functions current_streak_habit and current_streak_overview.

        Returns
        -------
        :return: int
            Returns a number as the streak count (zero to infinite)
            Gives it to the functions current_streak_habit and current_streak_overview to be displayed to the user.
        """
        existing_dates = self.get_tracking_data(habit_id)
        if existing_dates is None:
            return 0
        ref = datetime.now() - timedelta(days=1)
        items = []
        for item in reversed(existing_dates):
            item = datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S.%f')
            items.append(item)
        streak = 1 if datetime.now().date() == items[0].date() else 0

        for item in items[streak:]:
            if item.date() == ref.date():
                streak += 1
                ref -= timedelta(days=1)
            else:
                break

        return streak

    # COMPUTES THE CURRENT STREAK OF A HABIT WITH THE PERIODICITY WEEKLY
    def calculate_current_weekly_streak(self, habit_id):
        """
        Computes the current streak of a habit with the periodicity weekly.

        Function cannot be called directly by the user but is used within other functions.

        Parameters
        ----------
        :param habit_id: int
            Is assigned by the functions current_streak_habit and current_streak_overview.

        Returns
        -------
        :return: int
            Returns a number as the streak count (zero to infinite)
            Gives it to the functions current_streak_habit and current_streak_overview to be displayed to the user.
        """
        existing_dates = self.get_tracking_data(habit_id)
        if existing_dates is None:
            return 0

        # saves all dates in a list
        items = []
        for item in reversed(existing_dates):
            x = datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S.%f')
            items.append(x)

        # finds out which calendar week the stored data corresponds to
        calendar_weeks = []
        for n in range(0, len(items)):
            weeks = items[n].isocalendar()[1]
            calendar_weeks.append(weeks)

        # deletes all duplicate / same values, so that the calendar week is stored only once
        adj_calendar_weeks = []
        x = []
        for e in calendar_weeks:
            if e not in x:
                adj_calendar_weeks.append(e)
                x.append(e)

        now = datetime.now()
        now_week = now.isocalendar()[1]

        # computes the streak
        streak = []
        if len(adj_calendar_weeks) == 1:
            if adj_calendar_weeks[0] == now_week:
                streak.append(1)
                list_sum = sum(streak)
                return list_sum

        elif len(adj_calendar_weeks) >= 2 and adj_calendar_weeks[0] == now_week:
            streak.append(1)
            for n in range(0, len(adj_calendar_weeks)-1):
                x = adj_calendar_weeks[n] - adj_calendar_weeks[n + 1]
                if x == 1:
                    streak.append(1)
                else:
                    break
            list_sum = sum(streak)
            return list_sum
        else:
            return 0

    # RETURNS THE CURRENT STREAK OF A HABIT.
    # AUTOMATICALLY FILTERS IF THE HABIT IS A DAILY OR WEEKLY HABIT AND OUTPUTS THE DATA ACCORDINGLY.
    def current_streak_habit(self):
        """
        Returns the current streak of a specific habit.

        User is asked to enter the habit_id of a specific habit.
        If the habit_id exists, the function gets the periodicity of the habit.
        If the periodicity is 'Daily' it calls the function calculate_current_daily_streak,
        otherwise it calls the function calculate_current_weekly_streak.
        """
        habit_id = questionary.text("Please enter the ID of the habit for which "
                                    "you want to see the current streak? ",
                                    validate=lambda x: True if x.isdigit()
                                    else "Please enter a correct value.").ask()
        existing_habit = self.get_by_id(habit_id)
        periodicity = existing_habit.periodicity

        if existing_habit:
            if periodicity == "Daily":
                streak = self.calculate_current_daily_streak(habit_id)
                if streak is not None:
                    print(f"The current streak of the habit with the habit_id {habit_id} "
                          f"is: ", streak, " day(s)")
                else:
                    print("This habit does not exist.")

            else:
                streak = self.calculate_current_weekly_streak(habit_id)
                if streak is not None:
                    print(f"The current streak of the habit with the habit_id {habit_id} "
                          f"is: ", streak, " week(s)")
                else:
                    print("This habit does not exist.")
        else:
            print("This habit does not exist.")

    # Everything that has to do with the longest streak of the habits.

    # COMPUTES THE LONGEST STREAK OF A HABIT WITH THE PERIODICITY DAILY
    def calculate_longest_daily_streak(self, habit_id):
        """
        Calculates the longest streak of a habit with the periodicity daily.

        Pulls all tracking data for a specific habit from the database, stores and cleans the data in a list.
        Subtracts the values from each other. The differences are saved in a new list. The streak is calculated
        if the number is a 1, otherwise the loop breaks, then the maximum streak count is determined.

        Parameters
        ----------
        :param habit_id: int
            Is assigned through the functions longest_streak_habit() and longest_streak_overview()

        Returns
        -------
        :return: int
             Returns a number from 0 to infinite (max_value) as the longest streak count.
        """
        existing_dates = self.get_tracking_data(habit_id)
        if existing_dates is None:
            return 0

        items = []
        for item in reversed(existing_dates):
            item = datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S.%f')
            items.append(item)

        # calculates the difference between the values
        diff = []
        streak = 1 if datetime.now().date() == items[0].date() else 0
        diff.append(streak)

        for n in range(0, len(items) - 1):
            difference = items[n].date() - items[n + 1].date()
            diff.append(difference.days)

        # cleans up the differences in the list for easier reuse
        adj_diff = [99]
        for n in diff:
            if n == 1:
                adj_diff.append(1)
            elif n == 0 and adj_diff[-1] != 0:
                adj_diff.append(0)
            elif n != 0:
                adj_diff.append(99)

        temp_diff = []
        for i in range(1, len(adj_diff) - 1):
            if adj_diff[i] == 99 and adj_diff[i + 1] == 1:
                temp_diff.append(99)
                temp_diff.append(1)
            else:
                temp_diff.append(adj_diff[i])

        final_diff = temp_diff + adj_diff[-1:]

        for i in range(len(final_diff)):
            if final_diff[i] == 0:
                final_diff[i] = 1

        # calculates the streak
        # stores the values in the cache until a 99 appears
        # then the loop breaks, the values are summed and the max. value is output
        streak_count = []
        cache = []
        for n in final_diff:
            if n == 1:
                cache.append(1)
            else:
                list_sum = sum(cache)
                streak_count.append(list_sum)
                cache.clear()
                continue
        list_sum = sum(cache)
        streak_count.append(list_sum)

        max_value = max(streak_count)
        return max_value

    # COMPUTES THE LONGEST STREAK OF A HABIT WITH THE PERIODICITY WEEKLY
    def calculate_longest_weekly_streak(self, habit_id):
        """
        Calculates the longest streak of a habit with the periodicity weekly.

        Pulls all tracking data from the database, stores and cleans the data in a list.
        Subtracts the values from each other. The differences are saved in a new list.
        The streak is calculated and the maximum streak count is returned.

        Parameters
        ----------
        :param habit_id: int
            Is assigned through the functions longest_streak_habit() and longest_streak_overview()

        Returns
        -------
        :return: int
             Returns a number from 0 to infinite (max_value) as the longest streak count.
        """
        existing_dates = self.get_tracking_data(habit_id)
        if existing_dates is None:
            return 0

        items = []
        for item in reversed(existing_dates):
            item = datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S.%f')
            items.append(item)

        # finds out which calendar week the stored data corresponds to
        calendar_weeks = []
        for n in range(0, len(items)):
            weeks = items[n].isocalendar()[1]
            calendar_weeks.append(weeks)

        # deletes all duplicate / same values, so that the calendar week is stored only once
        adj_calendar_weeks = []
        x = []
        for e in calendar_weeks:
            if e not in x:
                adj_calendar_weeks.append(e)
                x.append(e)

        # computes the difference between the calendar weeks
        diff = [1]
        for n in range(0, len(adj_calendar_weeks) - 1):
            x = adj_calendar_weeks[n] - adj_calendar_weeks[n + 1]
            diff.append(x)

        if len(adj_calendar_weeks) >= 2:
            if adj_calendar_weeks[-1] != adj_calendar_weeks[-2]:
                diff.append(1)

            adj_diff = [1]
            for i in range(1, len(diff) - 1):
                if diff[i] > 1 and diff[i + 1] == 1:
                    adj_diff.append(99)
                    adj_diff.append(1)
                else:
                    adj_diff.append(diff[i])

            # calculates the streak
            # stores the values in the cache until a 99 appears
            # then the loop breaks, the values are summed and the max. value is output
            streak_count = []
            cache = []
            for n in adj_diff:
                if n == 1:
                    cache.append(1)
                else:
                    list_sum = sum(cache)
                    streak_count.append(list_sum)
                    cache.clear()
                    continue
            list_sum = sum(cache)
            streak_count.append(list_sum)

            max_value = max(streak_count)
            return max_value
        else:
            return 1

    # SHOWS THE USER THEIR LONGEST STREAK OF ALL THEIR HABITS SORTED BY PERIODICITY
    def longest_streak_overview(self):
        """
        Shows the user their longest streak of all their habits sorted by periodicity.

        First selects all daily habits from the database, then computes the longest streak from all habits
        and then prints the longest one to the user.

        Then selects all weekly habits from the database, then computes the longest streak from all habits
        and then prints the longest one to the user.
        """
        # daily habits
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM habit WHERE periodicity = 'Daily'
            """, (self.periodicity,))
            all_daily_habits = cursor.fetchall()
            daily_habits = []
            for habit in all_daily_habits:
                daily_habits.append(habit)

        streaks = []
        for habit in daily_habits:
            longest_daily_habit_streak = self.calculate_longest_daily_streak(habit[0])
            streaks.append((habit[0], longest_daily_habit_streak))

        max_value = max(streaks, key=lambda e: e[1])
        print(f"Your longest daily streak among all your daily habits is {max_value[1]} day(s). "
              f"The habit '{max_value[0]}' is your strongest!")

        # weekly habits
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM habit WHERE periodicity = 'Weekly'
            """, (self.periodicity,))
            all_weekly_habits = cursor.fetchall()
            weekly_habits = []
            for habit in all_weekly_habits:
                weekly_habits.append(habit)

        streaks = []
        for habit in weekly_habits:
            longest_weekly_habit_streak = self.calculate_longest_weekly_streak(habit[0])
            streaks.append((habit[0], longest_weekly_habit_streak))

        max_value = max(streaks, key=lambda e: e[1])
        print(f"Your longest weekly streak among all your weekly habits is {max_value[1]} weeks(s). "
              f"You're doing great with habit '{max_value[0]}'!")

    # The following are the functions that give an overview of all the habits.

    # ASKS THE USER FOR WHICH HABIT THEY WANT TO SEE THE LONGEST STREAK.
    # THEN SHOWS THE LONGEST STREAK FOR THE CHOSEN HABIT.
    # AUTOMATICALLY FILTERS IF THE HABIT IS DAILY OR WEEKLY.
    def longest_streak_habit(self):
        """
        Shows the longest streak for a chosen habit.

        User is asked to enter the habit_id of a specific habit.
        If the habit_id exists, the function gets the periodicity of the habit.
        If the periodicity is 'Daily' it calls the function calculate_longest_daily_streak,
        otherwise it calls the function calculate_longest_weekly_streak.
        """
        habit_id = questionary.text("Please enter the ID of the habit for which "
                                    "you want to see the longest streak? ",
                                    validate=lambda x: True if x.isdigit()
                                    else "Please enter a correct value.").ask()
        existing_habit = self.get_by_id(habit_id)
        periodicity = existing_habit.periodicity

        if existing_habit:
            if periodicity == "Daily":
                streak = self.calculate_longest_daily_streak(habit_id)
                if streak is not None:
                    print(f"The longest streak of the habit with the habit_id {habit_id} "
                          "is: ", streak, " day(s)")
            else:
                streak = self.calculate_longest_weekly_streak(habit_id)
                if streak is not None:
                    print(f"The longest streak of the habit with the habit_id {habit_id} "
                          "is: ", streak, " week(s)")

        else:
            print("This habit does not exist.")

    # QUERIES THE DB AND RETURNS A LIST OF ALL HABITS TO THE USER.
    def get_habits(self):
        """
        Queries the database and prints a list of all habits to the user.

        Returns
        -------
        :return: list
        returns a list of all habits
        """
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT name FROM habit""", (self.name,))
            items = cursor.fetchall()
            habits = []
            for item in items:
                habits.append(item[0])
            print(habits)
            return habits

    # QUERIES THE DB AND RETURNS A LIST OF ALL WEEKLY HABITS TO THE USER.
    def get_weekly_habits(self):
        """
        Queries the database and returns a list of all the weekly habits to the user.

        Returns
        -------
        :return: list
            returns a list of weekly habits
        """

        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM habit WHERE periodicity = 'Weekly'
            """, (self.periodicity,))
            items = cursor.fetchall()
            habits = []
            for item in items:
                habits.append(item[0])
            print(habits)
            return habits

    # QUERIES THE DB AND RETURNS A LIST OF ALL DAILY HABITS TO THE USER.
    def get_daily_habits(self):
        """
        Queries the database and returns a list of the daily habits to the user.

        Returns
        -------
        :return: list
            returns a list of all daily habits
        """
        with sqlite3.connect(self._DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM habit WHERE periodicity = 'Daily'
            """, (self.periodicity,))
            items = cursor.fetchall()
            habits = []
            for item in items:
                habits.append(item[0])
            print(habits)
            return habits
