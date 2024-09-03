import requests
import sqlite3
from datetime import datetime, timedelta

def get_most_recent_price():
    # Connect to the SQLite database
    conn = sqlite3.connect('energy_data.db')
    cursor = conn.cursor()
    
    # Query to get the top records
    cursor.execute('''
        SELECT period_start, period_end, price 
        FROM energy_prices 
        ORDER BY period_start DESC 
        LIMIT 1
    ''')
    
    # Fetch all records
    records = cursor.fetchall()
    
    conn.close()
    return records[0]

def fetch_and_insert_records(start_date=None, end_date=None):
    """
    Gets the agile energy price from the octopus energy API and inserts into the
    database. Fetches all data between start_date and end_date where start_date < end_date.
    If no dates are provided the most recent week of data are requested.
    """
    # Get the API key to query from the Octopus energy API
    with open("api.key", "r") as f:
        API_KEY = f.read()

    now = datetime.utcnow()
    start_date = (now - timedelta(days=7)).strftime('%Y-%m-%dT%H:%MZ')
    end_date = now.strftime('%Y-%m-%dT%H:%MZ')
    url = f"https://api.octopus.energy/v1/products/AGILE-24-04-03/electricity-tariffs/E-1R-AGILE-24-04-03-A/standard-unit-rates/?page_size=100&period_from={start_date}&period_to={end_date}&order_by=period"

    # Send the request
    response = requests.get(url, auth=(API_KEY, ''))
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    # Save data to the SQLite database
    conn = sqlite3.connect('energy_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS energy_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_start DATETIME NOT NULL,
        period_end DATETIME NOT NULL,
        price DECIMAL(10, 5) NOT NULL,
        UNIQUE(period_start, period_end)
    )''')

    # Insert records into the relevant table
    for record in data['results']:
        price = record['value_exc_vat'] # Price per kWh of electricity in pence excluding VAT
        time_start = datetime.strptime(record['valid_from'], '%Y-%m-%dT%H:%M:%SZ')
        time_end = datetime.strptime(record['valid_to'], '%Y-%m-%dT%H:%M:%SZ')

        # Insert the record into the database if a record with the same start/end period does not already exist
        cursor.execute('''
            INSERT OR IGNORE INTO energy_prices (period_start, period_end, price) 
            VALUES (?, ?, ?)
        ''', (time_start, time_end, price))
        
    # Commit and close
    conn.commit()
    conn.close()


def get_top_records(limit=5):
    """
    Fetch the most recent N records from the energy prices table
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('energy_data.db')
    cursor = conn.cursor()
    
    # Query to get the top records
    cursor.execute('''
        SELECT period_start, period_end, price 
        FROM energy_prices 
        ORDER BY period_start DESC 
        LIMIT ?
    ''', (limit,))
    
    # Fetch all records
    records = cursor.fetchall()
    
    conn.close()
    return records