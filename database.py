import sqlite3

def get_connection():
    conn = sqlite3.connect("unlock.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_title TEXT NOT NULL,
            company TEXT,
            source_url TEXT,
            priority TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS target_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            FOREIGN KEY (target_id) REFERENCES targets (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS my_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL UNIQUE,
            level INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_title TEXT NOT NULL,
            company TEXT,
            date_applied TEXT,
            status TEXT NOT NULL DEFAULT 'Saved',
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")