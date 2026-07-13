import yfinance as yf
from curl_cffi import requests


def get_market_cap(ticker):
    """Fetches the live market capitalization for a given ticker."""

    if not ticker or "PRIVATE" in ticker:
        return 0.0

    try:
        # Create a custom web session that explicitly ignores the NAS's broken SSL checks
        session = requests.Session(impersonate="chrome", verify=False)
        session.verify = False

        # Pass the custom session into Yahoo Finance
        stock = yf.Ticker(ticker, session=session)
        mcap = stock.info.get("marketCap", 0.0)

        return float(mcap)

    except Exception as e:
        print(f"⚠️ Failed to fetch Market Cap for {ticker}. Error: {e}")
        return 0.0