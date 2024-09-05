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

def get_last_week_usage():
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()

    last_week = datetime.utcnow() - timedelta(days=7)

    cursor.execute('''
        SELECT DATE(period_start), SUM(usage)
        FROM electricity_usage
        WHERE period_start >= ?
        GROUP BY DATE(period_start)
        ORDER BY DATE(period_start) ASC
    ''', (last_week, ))

    records = cursor.fetchall()

    # Extracting the date and total price for each day
    X = [parser.parse(record[0]).strftime("%a") for record in records]
    y = [record[1] for record in records]

    conn.close()
    return X, y

def get_average_usage():
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()

    # Step 1: Sum the usage for each day and calculate the average for each day of the week
    cursor.execute('''
        SELECT strftime('%w', date) AS day_of_week, AVG(daily_usage)
        FROM (
            SELECT DATE(period_start) AS date, SUM(usage) AS daily_usage
            FROM electricity_usage
            GROUP BY date
        )
        GROUP BY day_of_week
        ORDER BY day_of_week ASC
    ''')

    # Fetch all the results (7 records, one for each day of the week)
    records = cursor.fetchall()
    conn.close()

    # Map day_of_week from numbers (0-6) to weekday names (Sun-Sat)
    day_map = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    # Get today's day of the week
    today = datetime.utcnow().weekday()  # Monday=0, Sunday=6

    # Reorder the days to start with the day after today and include the next 7 days
    ordered_day_map = day_map[today+1:] + day_map[:today+1]

    # Create empty lists for X and y
    X, y = [], []

    # Reorder the records according to the ordered_day_map
    for day in ordered_day_map:
        for record in records:
            # Get the day of week name for the record
            record_day = day_map[int(record[0])]

            # Append if the days match
            if record_day == day:
                X.append(record_day)
                y.append(record[1])

    return X, y
