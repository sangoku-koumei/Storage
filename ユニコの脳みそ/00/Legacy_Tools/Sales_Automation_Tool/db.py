
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "sales_crm.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create companies table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            industry TEXT,
            status TEXT DEFAULT 'Generated',
            email_content TEXT,
            vision_summary TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_company(name, url, industry, email_content, vision_summary):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO companies (name, url, industry, email_content, vision_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, url, industry, email_content, vision_summary, datetime.now()))
    conn.commit()
    conn.close()

def get_all_companies():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM companies ORDER BY created_at DESC", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

def update_status(company_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE companies SET status = ? WHERE id = ?", (new_status, company_id))
    conn.commit()
    conn.close()
