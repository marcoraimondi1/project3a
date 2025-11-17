from datetime import datetime

API_KEY = "1L6IIQFIPW0YRYPC"

def filter_data_by_date(json_data, start_date, end_date):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except Exception:
        print("Error: Date should be in YYYY-MM-DD")
        return None
    end = end_date
    begin = start_date
    if end < begin:
        print("Error: End date must be after start date")
        return
    
    time_series_key = None

    if "Time Series (Daily)" in json_data:
        time_series_key = "Time Series (Daily)"
    elif "Weekly Time Series" in json_data:
        time_series_key = "Weekly Time Series"
    elif "Monthly Time Series" in json_data:
        time_series_key = "Monthly Time Series"
    elif "Time Series (5min)" in json_data:
        time_series_key = "Time Series (5min)"
    elif "Time Series (15min)" in json_data:
        time_series_key = "Time Series (15min)"
    elif "Time Series (30min)" in json_data:
        time_series_key = "Time Series (30min)"
    elif "Time Series (60min)" in json_data:
        time_series_key = "Time Series (60min)"
    elif "Time Series (1min)" in json_data:
        time_series_key = "Time Series (1min)"

    if time_series_key == None:
        print("Error: Time series data could not be found")
        return None
    
    time_series_data = json_data[time_series_key]

    data_filtered = {}

    for date_string in time_series_data:
        try:
            if 'Time Series' in time_series_key and 'min' in time_series_key:
                date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").date()
            else:
                date = datetime.strptime(date_string, "%Y-%m-%d").date()
        except Exception:
            continue

        if begin <= date <= end:
            data_filtered[date_string] = time_series_data[date_string]

    if len(data_filtered) == 0:
        print("Error: No data was found in the date range")
        return None
        
    result = {}

    if "Meta Data" in json_data:
        result["Meta Data"] = json_data["Meta Data"]

    result[time_series_key] = data_filtered
    
    return result

def print_data_filtered(data_filtered):
    time_series_key = None
    
    if "Time Series (Daily)" in data_filtered:
        time_series_key = "Time Series (Daily)"
    elif "Weekly Time Series" in data_filtered:
        time_series_key = "Weekly Time Series"
    elif "Monthly Time Series" in data_filtered:
        time_series_key = "Monthly Time Series"
    elif "Time Series (5min)" in data_filtered:
        time_series_key = "Time Series (5min)"
    elif "Time Series (15min)" in data_filtered:
        time_series_key = "Time Series (15min)"
    elif "Time Series (30min)" in data_filtered:
        time_series_key = "Time Series (30min)"
    elif "Time Series (60min)" in data_filtered:
        time_series_key = "Time Series (60min)"
    elif "Time Series (1min)" in data_filtered:
        time_series_key = "Time Series (1min)"

    if time_series_key == None:
        print("Error: No time series data found in filtered data")
        return
    
    time_series = data_filtered[time_series_key]

    print("\n")
    print(f"Filtered Stock Data {time_series_key}")
    print("\n")

    dates = sorted(time_series.keys())

    for date in dates:
        print(f"{date}: {time_series[date]}")

    print(f"\nData points: {len(dates)}")