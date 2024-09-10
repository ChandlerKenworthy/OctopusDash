import sqlite3
from dateutil import parser
import pandas as pd
import numpy as np
import datetime
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import tensorflow as tf
from tensorflow.keras.models import load_model

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

def get_latest_window():
    """
    Fetches the data for the last 12 timesteps as required by the machine learning
    model used by TensorFlow to model the pricing data. Manipulates accordingly.
    """
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT period_start, price
        FROM energy_prices
        ORDER BY period_start DESC
        LIMIT 336
    ''') # Use limit 336 to have sufficient data for the 7 day rolling average

    records = cursor.fetchall()
    conn.close()

    df = pd.DataFrame({
        'period_start': [parser.parse(r[0]) for r in records],
        'price': [r[1] for r in records]
    })
    df.set_index('period_start', inplace=True)
    df['HourOfDay'] = df.index.hour
    df['DayOfWeek'] = df.index.day_of_week
    df['value_exc_vat_7dayMAV'] = df['price'].rolling(window=7*24*2, min_periods=7*24, center=True).mean()
    df['dprice'] = np.insert(np.diff(df['price']), 0, np.nan)
    df['ddprice'] = np.insert(np.diff(df['dprice']), 0, np.nan)
    # Drop the rows now containing NaNs
    df = df.dropna(axis=0)

    # Sort on the index such that the most historical date is first (iloc[0]) etc.
    df.sort_index(ascending=True, inplace=True)

    # Pre-processing, the same as the model was trained with
    # Fit and transform the scaler on the relevant column
    scaler = StandardScaler()
    scaler.fit(df[['price']])

    # Transform the entire DataFrame
    df_scaled = pd.DataFrame(data=scaler.transform(df[['price']]), columns=['price'])

    # Add other features back
    mmScaler = MinMaxScaler()
    feature_list = ['HourOfDay', 'DayOfWeek', 'value_exc_vat_7dayMAV', 'dprice', 'ddprice']
    mmScaler.fit(df[feature_list])

    df_other_scaled = pd.DataFrame(data=mmScaler.transform(df[feature_list]), columns=feature_list)
    df_scaled = pd.concat([df_scaled, df_other_scaled.reset_index(drop=True)], axis=1)
    df_scaled.index = df.index

    return df_scaled, scaler

def df_to_X_y(df, data_cols, target_col, window_size=10):
    """
    data_cols (arr): Indicies of columns to use as predictors
    target_col (str): What you are trying to predict
    window_size (int): The number of previous timesteps to use for forecasting
    """
    target_col_index = np.where(df.columns == target_col)[0].item()
    df_as_np = df.to_numpy()
    X = []
    y = []

    for i in range(len(df_as_np) - window_size): # Maintain in-bounds
        row = [[a] for a in df_as_np[i:i+window_size, data_cols]]
        X.append(row)
        label = df_as_np[i+5, target_col_index]
        y.append(label)

    return np.array(X), np.array(y)    

def make_preds(X, scaler):
    model = load_model('tariff_price_multivar_new.keras')
    predictions_scaled = model.predict(X)
    # Inverse transform them
    predictions = scaler.inverse_transform(predictions_scaled.flatten().reshape(-1, 1)).flatten()
    return predictions

def get_predictions_from_latest():
    df, scaler = get_latest_window() # collects and does simple preprocessing

    # Now, pivot dataframe ready for making predictions
    window_size = 12
    X, y = df_to_X_y(df, [0, 1, 2, 3, 4, 5], "price", window_size=window_size)
    X = X.reshape((X.shape[0], window_size, 6))
    preds = make_preds(X, scaler)

    # Recall the prediction at [i] is predicting the price at timestep [i+2]

    # Now get the true pricing data i.e. that from the dates[2:] to as late as possible!
    conn = sqlite3.connect("energy_data.db")
    cursor = conn.cursor()

    # Fetch latest true pricing info the the last day, should be <prediction dates
    cursor.execute('''
        SELECT period_start, price
        FROM energy_prices
        ORDER BY period_start DESC
        LIMIT 48
    ''')

    records = cursor.fetchall()
    conn.close()

    truth_prices = [r[1] for r in records][::-1]
    truth_dates = [parser.parse(record[0]).strftime("%d-%m-%Y %H:%M") for record in records][::-1]

    # Parse the last date from the list
    last_date_str = truth_dates[-1]
    last_date = parser.parse(last_date_str)

    # Define the number of intervals to add (2 intervals of 30 minutes each)
    intervals_to_add = 2
    interval_duration = datetime.timedelta(minutes=30)

    # Extend the list with new dates
    for _ in range(intervals_to_add):
        last_date += interval_duration
        new_date_str = last_date.strftime("%d-%m-%Y %H:%M")
        truth_dates.append(new_date_str)

    # Predictions is currently quite long, preds[0] is the most recent prediction and preds[1]
    # the next most recent prediction

    # End of truth prices/truth dates 
    # remember preds[0] --> truth_prices[2]
    return preds, truth_prices, truth_dates