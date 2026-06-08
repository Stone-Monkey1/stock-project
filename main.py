from tools.gov_tools import fetch_and_map_contracts
from tools.scoring import calculate_urgency_score
from tools.market_tools import get_market_cap
import time  # Needed to pause between Yahoo Finance requests


def run_program():
    print("Starting Quantitative Contract Tracker...")

    # 1. Go get the data (this runs your API calls and returns the DataFrame)
    contract_df = fetch_and_map_contracts()

    if contract_df is None or contract_df.empty:
        print("No data to process.")
        return

    # 2. Get all unique tickers from the DataFrame
    unique_tickers = contract_df["Ticker"].unique()

    # Filter out the "PRIVATE / UNKNOWN" entries so we only score real stocks
    public_tickers = [
        ticker for ticker in unique_tickers if "PRIVATE" not in str(ticker)
    ]

    print(f"\n📊 Found {len(public_tickers)} public companies to score!")

    # 3. Loop through EACH public ticker one by one
    for ticker in public_tickers:

        # Get the market cap for this specific company
        market_cap = get_market_cap(ticker)

        # Safety net: Skip scoring if Yahoo Finance couldn't find the market cap
        if market_cap == 0.0:
            print(f"⚠️ Skipping {ticker} - Could not retrieve Market Cap.")
            continue

        # Feed the SINGLE ticker, data, and market cap into your algorithm
        score = calculate_urgency_score(ticker, contract_df, market_cap)

        print(f"📈 Urgency Score for {ticker}: {score:.8f}")

        # Be polite to Yahoo Finance servers by pausing for 1 second between requests
        time.sleep(1)


if __name__ == "__main__":
    run_program()
