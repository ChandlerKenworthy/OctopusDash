import sqlite3
from datetime import datetime, timedelta
from dateutil import parser

def get_curr_usage():
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT usage, period_start, period_end
        FROM electricity_usage
        ORDER BY period_start DESC
        LIMIT 1
    ''')

    records = cursor.fetchall()
    conn.close()
    return records[0]