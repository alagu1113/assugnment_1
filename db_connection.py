import mysql.connector
import pandas as pd
from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Thrasher@49",
    "database": "cricket"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # indian_players
    cur.execute('''
    CREATE TABLE IF NOT EXISTS indian_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT,
        Role TEXT,
        BattingStyle TEXT,
        BowlingStyle TEXT
    )
    ''')

def execute(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    cursor.close()
    conn.close()

def read_sql(query, params=None):
    conn = get_connection()
    
    # If user forgets SELECT, add it
    if not query.strip().lower().startswith("select"):
        query = f"SELECT {query}"
    
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
