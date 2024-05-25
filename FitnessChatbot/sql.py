import sqlite3

# Connect to SQLite database
connection = sqlite3.connect('fitness.db')

# Create a cursor object
cursor = connection.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS GlucoseLevel (
    Date TEXT PRIMARY KEY,
    Level INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS StepCount (
    Date TEXT PRIMARY KEY,
    Steps INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS HeartRate (
    Date TEXT PRIMARY KEY,
    Rate INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS CalorieTracking (
    Date TEXT PRIMARY KEY,
    Calories INTEGER
);
""")

##########################################################################
## CUSTOM DATA FOR TIME BEING



# Insert some predefined values
glucose_values = [
    ("2023-05-20", 120),
    ("2023-05-21", 130),
    ("2023-05-22", 135)
]

step_count_values = [
    ("2023-05-20", 8000),
    ("2023-05-21", 6000),
    ("2023-05-22", 7000)
]

calorie_tracking_values = [
    ("2023-05-20", 2500),
    ("2023-05-21", 2000),
    ("2023-05-22", 2200)
]

cursor.executemany("INSERT OR IGNORE INTO GlucoseLevel (Date, Level) VALUES (?, ?)", glucose_values)
cursor.executemany("INSERT OR IGNORE INTO StepCount (Date, Steps) VALUES (?, ?)", step_count_values)
cursor.executemany("INSERT OR IGNORE INTO CalorieTracking (Date, Calories) VALUES (?, ?)", calorie_tracking_values)
############################################################################

# Close the connection
connection.commit()
connection.close()
