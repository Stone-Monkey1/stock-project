import yfinance as yf
import time
import os
import certifi

os.environ["CURL_CA_BUNDLE"] = certifi.where()


def get_market_cap(ticker):
    """Fetches the live market capitalization for a given ticker."""

    # If the ticker is empty or our "PRIVATE" fallback, skip it
    if not ticker or "PRIVATE" in ticker:
        return 0.0

    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker)

        # .info is a massive dictionary containing all of Yahoo Finance's data
        # We use .get() so it safely returns 0 if the data is missing
        mcap = stock.info.get("marketCap", 0.0)

        return float(mcap)

    except Exception as e:
        print(f"⚠️ Failed to fetch Market Cap for {ticker}. Error: {e}")
        return 0.0
