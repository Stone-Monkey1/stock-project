import yfinance as yf
import os

os.environ["CURL_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"
os.environ["REQUESTS_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"
os.environ["SSL_CERT_FILE"] = "/etc/ssl/certs/ca-certificates.crt"


def get_market_cap(ticker):
    """Fetches the live market capitalization for a given ticker."""

    if not ticker or "PRIVATE" in ticker:
        return 0.0

    try:
        stock = yf.Ticker(ticker)
        mcap = stock.info.get("marketCap", 0.0)
        return float(mcap)

    except Exception as e:
        print(f"⚠️ Failed to fetch Market Cap for {ticker}. Error: {e}")
        return 0.0
