import sqlite3

def init_db():
    conn = sqlite3.connect("certificates.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        course_name TEXT,
        issuer TEXT,
        certificate_hash TEXT,
        previous_hash TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()
    