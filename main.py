import questionary
import sqlite3
from habit import Habit
from datetime import datetime, timedelta


def main_menu():
    choice = questionary.select(
        "What do you want to do?",
        choices=[
            "Create a new habit",
            "Edit an existing habit",
            "Delete a habit",
            "Mark a habit as completed",
            "Show all habits",
            "Show all weekly habits",
            "Show all daily habits",
            "Show current streak per habit",
            "Show longest streak per habit",
            "Show longest streak overview (by periodicity)",
            "Exit"
        ]
    ).ask()

    if choice == "Create a new habit":
        create_habit()
    elif choice == "Edit an existing habit":
        edit_habit()
    elif choice == "Delete a habit":
        delete_habit()
    elif choice == "Mark a habit as completed":
        mark_habit_as_completed()
    elif choice == "Show all habits":
        show_all_habits()
    elif choice == "Show all weekly habits":
        show_all_weekly_habits()
    elif choice == "Show all daily habits":
        show_all_daily_habits()
    elif choice == "Show current streak per habit":
        show_current_streak_per_habit()
    elif choice == "Show longest streak per habit":
        show_longest_streak_per_habit()
    elif choice == "Show longest streak overview (by periodicity)":
        show_longest_streak_overview()
    elif choice == "Exit":
        exit()


def create_habit():
    habit_id = questionary.text("Please enter an ID for your habit:",
                                validate=lambda x: True if x.isdigit()
                                else "Please enter a correct value."
                                ).ask()
    name = questionary.text("Please enter the habit name:",
                            validate=lambda text: True if len(text) > 0 and text.isalpha()
                            else "Please enter a correct value. "
                            "Your habit name should only contain upper and lowercase letters."
                            ).ask()
    description = questionary.text("Please enter the habit description:").ask()
    periodicity = questionary.text(
        "Is your habit a daily or a weekly habit? You can choose between `Daily` and `Weekly`.",
    ).ask()

    habit = Habit(habit_id=habit_id, name=name, description=description, periodicity=periodicity)
    habit.save()
    print("Habit saved successfully!")
    main_menu()


def edit_habit():
    habit_id = questionary.text("Please enter the ID of the habit to edit:",
                                validate=lambda x: True if x.isdigit()
                                else "Please enter a correct value.").ask()
    habit = Habit.get_by_id(habit_id)

    if not habit:
        print("Habit not found!")
        main_menu()
        return

    name = questionary.text(f"Please enter the new name (current: {habit.name}):").ask()
    description = questionary.text(f"Please enter the new description (current: {habit.description}):").ask()
    periodicity = questionary.text(f" Please enter the new periodicity (current: {habit.periodicity}):").ask()

    habit = Habit(name=name, description=description, periodicity=periodicity)
    habit.save()
    print("Habit updated successfully!")
    main_menu()


def delete_habit():
    habit_id = questionary.text("Please enter the ID of the habit to delete:",
                                validate=lambda x: True if x.isdigit()
                                else "Please enter a correct value.").ask()
    habit = Habit.get_by_id(habit_id)

    if not habit:
        print("Habit not found!")
        main_menu()
        return

    confirmation = questionary.confirm(f"Are you sure you want to delete habit ´{habit.name}´?").ask()
    if confirmation:
        habit.delete_habit()
        print("Habit deleted successfully!")
    main_menu()


def mark_habit_as_completed():
    habit_id = questionary.text("Please enter the ID of the habit you want to mark as completed:",
                                validate=lambda x: True if x.isdigit()
                                else "Please enter a correct value.").ask()
    habit = Habit.get_by_id(habit_id)

    if not habit:
        print("Habit not found!")
        main_menu()
        return

    habit.mark_completed()
    habit.save()
    print("You completed your habit. Well done!")
    main_menu()


def show_all_habits():
    print("You currently have these habits saved:")
    habit = Habit()
    habit.get_weekly_habits()
    main_menu()


def show_all_weekly_habits():
    print("Your weekly habits are:")
    habit = Habit()
    habit.get_weekly_habits()
    main_menu()


def show_all_daily_habits():
    print("Your daily habits are:")
    habit = Habit()
    habit.get_daily_habits()
    main_menu()


def show_current_streak_per_habit():
    habit = Habit()
    habit.current_streak_habit()
    main_menu()


def show_longest_streak_per_habit():
    habit = Habit()
    habit.longest_streak_habit()
    main_menu()


def show_longest_streak_overview():
    habit = Habit()
    habit.longest_streak_overview()
    main_menu()


# EXECUTES THE FUNCTION DEFINED ABOVE AND STARTS THE USER GUIDANCE.
main_menu()
