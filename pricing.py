import sqlite3
from datetime import datetime, timedelta
from dateutil import parser

def get_last_day_pricing_by_hour():
    # Connect to the SQLite database
    conn = sqlite3.connect('energy_data.db')
    cursor = conn.cursor()
    
    # Query to get the top records
    cursor.execute('''
        SELECT strftime('%Y-%m-%d %H:00', period_start) as hourly_period, AVG(price)
        FROM energy_prices 
        GROUP BY hourly_period
        ORDER BY hourly_period DESC
        LIMIT 24
    ''')
    
    # Fetch all records
    records = cursor.fetchall()
    hourly_avg_price = [r[1] for r in records]
    conn.close()
    
    return hourly_avg_price[::-1]