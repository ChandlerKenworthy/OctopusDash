from flask import Flask, render_template, jsonify
from db import get_top_records, fetch_electricity_pricing, get_most_recent_price, get_curr_price_percentage_change, fetch_electricity_usage
from datetime import datetime, timedelta
from dateutil import parser
from usage import get_curr_usage, get_last_week_usage, get_average_usage

app = Flask(__name__)

@app.route('/')
def index():
    # Get top 5 records
    records = get_top_records(50)
    curr_info = get_most_recent_price()
    curr_usage_info = get_curr_usage()
    curr_price_change = get_curr_price_percentage_change(curr_info[2])
    last_week_dates, last_week_usage = get_last_week_usage()
    days_avg, usage_avg = get_average_usage()

    # Reformat the datetime object to the desired format
    most_recent_datetime = datetime.strptime(curr_info[1], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")

    return render_template(
        'index.html', 
        records=records, 
        current_price=curr_info[2],
        curr_usage=curr_usage_info[0],
        usage_start=parser.parse(curr_usage_info[1]).strftime("%d/%m %H:%M"),
        usage_end=parser.parse(curr_usage_info[2]).strftime("%d/%m %H:%M"),
        curr_price_pct_change_week=curr_price_change,
        most_recent_data_fetch_date=most_recent_datetime,
        last_week_dates=last_week_dates,
        last_week_usage=last_week_usage,
        days_avg=days_avg,
        usage_avg=usage_avg
    )

@app.route('/get_more_data', methods=['POST'])
def get_more_data():
    try:
        # Call the get_more_data function to fetch new data

        # TODO: Make these values from a form the user submits to change date range?
        now = datetime.utcnow()
        start_date = (now - timedelta(days=100)).strftime('%Y-%m-%dT%H:%MZ')
        end_date = now.strftime('%Y-%m-%dT%H:%MZ')
        fetch_electricity_pricing(start_date, end_date)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error fetching more data: {e}")
        return jsonify({"success": False}), 500
    
@app.route('/get_usage_data', methods=['POST'])
def get_usage_data():
    try:
        now = datetime.utcnow()
        start_date = (now - timedelta(days=7)).strftime('%Y-%m-%dT%H:%MZ')
        end_date = now.strftime('%Y-%m-%dT%H:%MZ')
        fetch_electricity_usage(start_date, end_date)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error fetching more data: {e}")
        return jsonify({"success": False}), 500

if __name__ == '__main__':
    app.run(debug=True)