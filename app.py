from flask import Flask, render_template, jsonify
from db import get_top_records, fetch_and_insert_records, get_most_recent_price
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    # Get top 5 records
    records = get_top_records(50)
    curr_info = get_most_recent_price()

    return render_template(
        'index.html', 
        records=records, 
        current_price=curr_info[2],
        most_recent_data_fetch_date=curr_info[1]
    )

@app.route('/get_more_data', methods=['POST'])
def get_more_data():
    try:
        # Call the get_more_data function to fetch new data

        # TODO: Make these values from a form the user submits to change date range?
        now = datetime.utcnow()
        start_date = (now - timedelta(days=100)).strftime('%Y-%m-%dT%H:%MZ')
        end_date = now.strftime('%Y-%m-%dT%H:%MZ')
        fetch_and_insert_records(start_date, end_date)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error fetching more data: {e}")
        return jsonify({"success": False}), 500

if __name__ == '__main__':
    app.run(debug=True)