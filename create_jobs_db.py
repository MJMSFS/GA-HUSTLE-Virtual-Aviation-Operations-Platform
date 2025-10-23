import sqlite3
import os

# Ensure the 'database' folder exists
os.makedirs('database', exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect('database/jobs.db')
cursor = conn.cursor()

# Create the 'jobs' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,
    passengers INTEGER DEFAULT NULL,
    cargo_weight REAL DEFAULT NULL,
    departure_airport TEXT NOT NULL,
    destination_airport TEXT NOT NULL,
    reward REAL NOT NULL,
    time_limit INTEGER DEFAULT NULL,
    description TEXT DEFAULT NULL
)
''')

# Insert sample job data
sample_data = [
    ('Air Taxi', 1, None, 'LECU', 'LESA', 500, 2, 'VIP passenger - priority service'),
    ('Air Taxi', 3, None, 'LEBL', 'LEZL', 800, None, 'Family trip, flexible timing'),
    ('Cargo', None, 150, 'LEMD', 'LEBC', 700, 4, 'Deliver electronics - urgent'),
    ('Cargo', None, 400, 'LEMG', 'LEBI', 1200, None, 'Transport machinery - standard delivery'),
    ('Air Taxi', 2, None, 'LECU', 'LESA', 800, 3, 'VIP passengers, urgent delivery.'),
    ('Cargo', None, 300, 'LEMD', 'LEGR', 900, 5, 'Electronics delivery, standard priority.'),
    ('Cargo', None, 500, 'LEMG', 'LEBI', 700, None, 'Vacation freight, urgent trip.'),
    ('Air Taxi', 1, None, 'LECU', 'LESA', 600, 2, 'Business passengers, urgent delivery.'),
    ('Air Taxi', 3, None, 'LEBL', 'LEGR', 800, 3, 'Business passengers, urgent trip.'),
    ('Air Taxi', 1, None, 'LEMG', 'LEBI', 500, 2, 'VIP passenger, priority service.'),
    ('Air Taxi', 4, None, 'LEST', 'LEVC', 950, 4, 'Group trip, standard priority.'),
    ('Air Taxi', 2, None, 'LEVC', 'LEBI', 650, 3, 'Business passengers, urgent delivery.'),
    ('Cargo', None, 200, 'LEMD', 'LEBI', 700, 5, 'Deliver medical supplies, standard priority.'),
    ('Cargo', None, 300, 'LEGR', 'LEBC', 650, 6, 'Transport electronics, urgent delivery.'),
    ('Cargo', None, 150, 'LEVC', 'LEST', 800, 5, 'Deliver perishables, standard priority.'),
    ('Cargo', None, 400, 'LEBL', 'LEST', 1000, None, 'Transport machinery, flexible timing.'),
    ('Cargo', None, 250, 'LEJR', 'LEVC', 750, 3, 'Deliver spare parts, urgent delivery.')
]

cursor.executemany('''
INSERT INTO jobs (job_type, passengers, cargo_weight, departure_airport, destination_airport, reward, time_limit, description)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', sample_data)

# Commit changes and close connection
conn.commit()
conn.close()

print("Jobs table created and sample data inserted successfully!")