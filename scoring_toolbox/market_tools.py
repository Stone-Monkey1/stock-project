import yfinance as yf
import requests
import urllib3

# Mute the warnings that Python throws when you intentionally bypass SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_market_cap(ticker):
    """Fetches the live market capitalization for a given ticker."""

    # If the ticker is empty or our "PRIVATE" fallback, skip it
    if not ticker or "PRIVATE" in ticker:
        return 0.0

    try:
        # Create a custom web session that explicitly ignores SSL ID checks
        session = requests.Session()
        session.verify = False

        # Pass our custom "ignore security" session into Yahoo Finance
        stock = yf.Ticker(ticker, session=session)

        # .info is a massive dictionary containing all of Yahoo Finance's data
        mcap = stock.info.get("marketCap", 0.0)

        return float(mcap)

    except Exception as e:
        print(f"⚠️ Failed to fetch Market Cap for {ticker}. Error: {e}")
        return 0.0
