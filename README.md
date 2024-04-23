# Project: Habit Tracking App

Welcome to the prototype of my Habit Tracking App! 
With this App users can create, manage and analyze multiple habits.
Users are able to create habits with the periodicity "Daily" and "Weekly".
Please be aware that this application is still under construction. 
That means that some functionalities of the Habit Tracking App
may not work as they are supposed to right now. 
This problems will be solved in the ongoing construction process. 

## What are the functionalities of the Habit Tracking App?

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

### Create, edit and delete a habit:

The user can create a new habit by defining the id, the name, 
the description and the periodicity of a new habit.
The user can edit and delete an existing habit by its ID.

### Mark a habit as completed:

When the user marks a habit as completed, 
the current date and time is saved to the database 
and the streak of this habit is set to 1. 
When the user completes the habit twice a day 
the streak of this habit will still be 1.
A daily habit has to be completed once per day and
a weekly habit has to be completed once per calendar week.

### Show all habits, all weekly habits and all daily habits:

A list of the names of all currently tracked habits, 
all weekly habits and all daily habits is shown to the user.

### Show the current/longest streak per habit, show the longest streak overview:

When a task of a habit is completed x consecutive periods in a row 
without breaking the habit the user established a streak of x periods. 
The user can get the current/longest streak per habit and the longest streak
for all defined habits.

## Installation

First of all the files of the project folder need to be downloaded 
and added to your personal python IDE (python 3.7+ is required). 
After that all the libraries and tools listed in
the file requirements.txt need to be installed.

```shell
pip install -r requirements.txt
```

## Usage

Start the application by typing

```shell
python main.py
```

to your console and follow the instructions on screen.

## Tests

A unit test suite is provided for validation and testing purposes. 
Run the test by typing

```shell
pytest .
```

to your console.

## Contributing

This is my first Python project. For that reason I would be happy about comments, 
suggestions and contributions. 
