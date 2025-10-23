import sqlite3

# Connect to the pilots database (creates it if it doesn't exist)
conn = sqlite3.connect('database/pilots.db')
cursor = conn.cursor()

# Create the pilots table
cursor.execute('''
CREATE TABLE pilots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Pilots database and pilots table created successfully!")