import sqlite3

DATABASE_PILOTS = 'pilots.db'  # Make sure 'pilots.db' is in the correct path

def get_pilots_db():
    """Establishes and returns a connection to the pilots SQLite database."""
    conn = sqlite3.connect(DATABASE_PILOTS)
    conn.row_factory = sqlite3.Row  # Optional: Access columns by name
    return conn

def get_pilots_cursor(conn):
    """Returns a cursor object for the given SQLite connection."""
    cursor = conn.cursor()
    return cursor