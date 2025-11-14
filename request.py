import requests
from date_filter import filter_data_by_date


def makeRequest(
    func: str,
    symbol: str,
    apikey: str,
    start_date: str,
    end_date: str,
    interval: str | None = None,
):
    """Fetch stock data from AlphaVantage.

    Args:
        func: One of TIME_SERIES_MONTHLY, TIME_SERIES_INTRADAY, TIME_SERIES_DAILY, TIME_SERIES_WEEKLY.
        symbol: The stock ticker symbol.
        apikey: AlphaVantage API key.
        start_date: Beginning of the requested window (YYYY-MM-DD).
        end_date: End of the requested window (YYYY-MM-DD).
        interval: Required for intraday queries (1min, 5min, 15min, 30min, 60min).
    """

    params = {
        "function": func,
        "symbol": symbol,
        "apikey": apikey,
    }

    if interval:
        params["interval"] = interval

    response = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    return filter_data_by_date(data, start_date, end_date)


# To test the function (If you try to test daily further then 100 days ago it wont let you and will come back with a error)
# Pretty sure this is because we have the free tier so it has limits on it
'''
if __name__ == "__main__":
    API_KEY = "KST2CQHMXDNNVQAX"
    symbol = "IBM"
    func = "TIME_SERIES_DAILY"
    start_date = "2025-09-01"
    end_date = "2025-09-04"

    filtered_data = makeRequest(func, symbol, API_KEY, start_date, end_date)

    print_data_filtered(filtered_data)
'''
