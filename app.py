from flask import Flask, render_template, request, jsonify
from request import makeRequest
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart', methods=['POST'])
def get_chart_data():
    try:
        data = request.json
        
        if not data.get('symbol'):
            return jsonify({'error': 'Symbol is required'}), 400
        
        time_series_map = {
            'TIME_SERIES_INTRADAY': 'TIME_SERIES_INTRADAY',
            'TIME_SERIES_DAILY': 'TIME_SERIES_DAILY',
            'TIME_SERIES_WEEKLY': 'TIME_SERIES_WEEKLY',
            'TIME_SERIES_MONTHLY': 'TIME_SERIES_MONTHLY'
        }
        
        func = time_series_map.get(data.get('time_series'), 'TIME_SERIES_DAILY')
        symbol = data.get('symbol')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        interval = data.get('interval')
        
        api_key = os.getenv('ALPHAVANTAGE_KEY', '1L6IIQFIPW0YRYPC')
        
        stock_data = makeRequest(func, symbol, api_key, start_date, end_date, interval)
        
        if stock_data is None:
            return jsonify({'error': 'Failed to retrieve data'}), 400
        
        time_series_keys = [k for k in stock_data.keys() if k != 'Meta Data']
        if not time_series_keys:
            return jsonify({'error': 'No time series data found in response'}), 400
        
        time_series_key = time_series_keys[0]
        time_series_data = stock_data[time_series_key]
        
        dates = sorted(time_series_data.keys())
        
        open_values = []
        high_values = []
        low_values = []
        close_values = []
        
        for date in dates:
            try:
                open_values.append(float(time_series_data[date].get('1. open', 0)))
                high_values.append(float(time_series_data[date].get('2. high', 0)))
                low_values.append(float(time_series_data[date].get('3. low', 0)))
                close_values.append(float(time_series_data[date].get('4. close', 0)))
            except (ValueError, KeyError):
                continue
        
        return jsonify({
            'labels': dates,
            'open': open_values,
            'high': high_values,
            'low': low_values,
            'close': close_values
        })
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/chart', methods=['POST'])
def api_chart():
    return get_chart_data()

if __name__ == '__main__':
    app.run(host="0.0.0.0")