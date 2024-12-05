import sqlite3

def initialize_database():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            muscle_group TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            muscle_group TEXT NOT NULL,
            total_sets INTEGER NOT NULL,
            total_reps INTEGER NOT NULL,
            total_weight REAL NOT NULL
        )
    ''')

    connection.commit()
    connection.close()

def add_exercise(name, muscle_group, sets, reps, weight):
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO exercises (name, muscle_group, sets, reps, weight)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, muscle_group, sets, reps, weight))

    connection.commit()
    connection.close()

def get_exercises():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('SELECT name, muscle_group, sets, reps, weight FROM exercises')
    exercises = cursor.fetchall()
    connection.close()
    return exercises

def calculate_weekly_summary():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('''
        SELECT muscle_group, SUM(sets) as total_sets, SUM(reps) as total_reps, SUM(weight) as total_weight
        FROM exercises
        GROUP BY muscle_group
    ''')
    summary = cursor.fetchall()
    cursor.executemany('''
        INSERT INTO weekly_summary (week, muscle_group, total_sets, total_reps, total_weight)
        VALUES (strftime('%W', 'now'), ?, ?, ?, ?)
    ''', [(row[0], row[1], row[2], row[3]) for row in summary])
    connection.commit()
    connection.close()

def get_weekly_summary():
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('SELECT muscle_group, total_sets, total_reps, total_weight FROM weekly_summary')
    summary = cursor.fetchall()
    connection.close()
    return summary

def calculate_total_sets(muscle_group):
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('''
        SELECT SUM(sets) FROM exercises WHERE muscle_group = ?
    ''', (muscle_group,))
    total_sets = cursor.fetchone()[0] or 0
    connection.close()
    return total_sets

def calculate_fractional_sets(muscle_group):
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('''
        SELECT SUM(sets * weight / (SELECT SUM(weight) FROM exercises WHERE muscle_group = ?))
        FROM exercises
        WHERE muscle_group = ?
    ''', (muscle_group, muscle_group))
    fractional_sets = cursor.fetchone()[0] or 0
    connection.close()
    return fractional_sets

def calculate_direct_sets(muscle_group):
    connection = sqlite3.connect("workout.db")
    cursor = connection.cursor()
    cursor.execute('''
        SELECT SUM(sets) 
        FROM exercises
        WHERE muscle_group = ?
    ''', (muscle_group,))
    direct_sets = cursor.fetchone()[0] or 0
    connection.close()
    return direct_sets
