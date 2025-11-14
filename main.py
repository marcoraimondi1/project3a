from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from flask import Flask, render_template, request
from requests import HTTPError

from request import makeRequest

app = Flask(__name__)

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")

STOCK_SYMBOLS = [
    ("AAPL", "Apple (AAPL)"),
    ("GOOGL", "Alphabet (GOOGL)"),
    ("MSFT", "Microsoft (MSFT)"),
    ("AMZN", "Amazon (AMZN)"),
    ("IBM", "IBM (IBM)"),
    ("TSLA", "Tesla (TSLA)"),
]

CHART_TYPES = [
    ("bar", "1. Bar"),
    ("line", "2. Line"),
]

TIME_SERIES_OPTIONS = [
    ("TIME_SERIES_INTRADAY", "1. Intraday"),
    ("TIME_SERIES_DAILY", "2. Daily"),
    ("TIME_SERIES_WEEKLY", "3. Weekly"),
    ("TIME_SERIES_MONTHLY", "4. Monthly"),
]

INTRADAY_INTERVALS = [
    ("1min", "1 Minute"),
    ("5min", "5 Minutes"),
    ("15min", "15 Minutes"),
    ("30min", "30 Minutes"),
    ("60min", "60 Minutes"),
]


def _prepare_chart_data(data: dict[str, Any]) -> dict[str, list[float | str]] | None:
    series_key = next((key for key in data.keys() if key != "Meta Data"), None)
    if not series_key:
        return None

    ordered_dates = sorted(data[series_key].keys())

    def extract(value_key: str) -> list[float]:
        values: list[float] = []
        for date in ordered_dates:
            try:
                values.append(float(data[series_key][date][value_key]))
            except (KeyError, ValueError):
                values.append(0.0)
        return values

    return {
        "labels": ordered_dates,
        "open": extract("1. open"),
        "high": extract("2. high"),
        "low": extract("3. low"),
        "close": extract("4. close"),
    }


def _validate_dates(start_date: str, end_date: str) -> tuple[str, str] | tuple[None, None]:
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return None, None

    if end_obj < start_obj:
        return None, None

    return start_date, end_date


@app.route("/", methods=["GET", "POST"])
def index():
    chart_data: dict[str, list[float | str]] | None = None
    error: str | None = None

    form_data = {
        "symbol": STOCK_SYMBOLS[0][0],
        "chart_type": CHART_TYPES[1][0],
        "time_series": TIME_SERIES_OPTIONS[1][0],
        "interval": INTRADAY_INTERVALS[0][0],
        "start_date": "",
        "end_date": "",
    }

    if request.method == "POST":
        form_data.update({
            "symbol": request.form.get("symbol", form_data["symbol"]),
            "chart_type": request.form.get("chart_type", form_data["chart_type"]),
            "time_series": request.form.get("time_series", form_data["time_series"]),
            "interval": request.form.get("interval", form_data["interval"]),
            "start_date": request.form.get("start_date", ""),
            "end_date": request.form.get("end_date", ""),
        })

        start_date, end_date = _validate_dates(form_data["start_date"], form_data["end_date"])
        if not start_date or not end_date:
            error = "Please provide a valid date range in the format YYYY-MM-DD."
        else:
            interval = form_data["interval"] if form_data["time_series"] == "TIME_SERIES_INTRADAY" else None
            if form_data["time_series"] == "TIME_SERIES_INTRADAY" and not interval:
                error = "Select an interval for intraday data."
            else:
                try:
                    stock_data = makeRequest(
                        form_data["time_series"],
                        form_data["symbol"],
                        API_KEY,
                        start_date,
                        end_date,
                        interval,
                    )
                    if stock_data:
                        chart_data = _prepare_chart_data(stock_data)
                        if not chart_data:
                            error = "Unable to build chart from the provided data."
                    else:
                        error = "No data returned for the selected inputs. Try a different date range."
                except HTTPError as exc:  # pragma: no cover - network errors
                    error = f"Request failed: {exc}"  # pragma: no cover
                except Exception as exc:  # pragma: no cover
                    error = f"An unexpected error occurred: {exc}"  # pragma: no cover

    return render_template(
        "index.html",
        symbols=STOCK_SYMBOLS,
        chart_types=CHART_TYPES,
        time_series_options=TIME_SERIES_OPTIONS,
        intraday_intervals=INTRADAY_INTERVALS,
        chart_data=chart_data,
        chart_type=form_data["chart_type"],
        selected_symbol=form_data["symbol"],
        error=error,
        form_data=form_data,
    )


if __name__ == "__main__":
    app.run(port=5000, debug=False)