import sqlite3

def setup_ledger_db():
    conn = sqlite3.connect('database/ledger.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            datetime TEXT,
            pilot TEXT,
            income REAL,
            outgoing REAL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("ledger.db and table 'ledger' created successfully.")

if __name__ == "__main__":
    setup_ledger_db()