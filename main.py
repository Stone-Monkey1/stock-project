from tools.gov_tools import fetch_and_map_contracts
from tools.market_tools import get_market_cap
from tools.history_tools import load_scores, save_scores
from tools.scoring import calculate_daily_score, update_scoreboard
import time


def run_program():
    print("Starting Quantitative Contract Tracker...")

    # 1. Load the historical contract lists from JSON
    # It will look like {"LMT": [...], "BA": [...]}
    historical_data = load_scores()

    # 2. Fetch today's new data
    contract_df = fetch_and_map_contracts()

    if contract_df is None or contract_df.empty:
        print("No new data to process today.")
        todays_scores = {}
        return

    else:

        unique_tickers = contract_df["Ticker"].unique()
        public_tickers = [
            ticker for ticker in unique_tickers if "PRIVATE" not in str(ticker)
        ]

        # Dictionary to hold the final scores for printing
        todays_scores = {}

        print(f"\n📊 Processing {len(public_tickers)} public companies...")

        # 3. Loop through companies and update their rolling windows
        for ticker in public_tickers:
            market_cap = get_market_cap(ticker)

            # Isolate just the new contracts for this specific company
            company_new_contracts = contract_df[contract_df["Ticker"] == ticker]

            # Get their existing history from the JSON (or an empty list if they are new)
            daily_score = calculate_daily_score(company_new_contracts, market_cap)

            if daily_score > 0.0:
                todays_scores[ticker] = daily_score

            time.sleep(1)
    # 👉 Pass today's scores and the JSON history into the momentum mixer
    final_scoreboard = update_scoreboard(todays_scores, historical_data)

    # 4. Save the pruned historical data back to the hard drive
    save_scores(final_scoreboard)

    # 5. Print the Top 5
    print("\n🏆 --- TOP 5 TTM URGENCY SCORES --- 🏆")
    for i, (ticker, score) in enumerate(list(final_scoreboard.items())[:5]):
        print(f"{i+1}. {ticker}: {score:.6f}")


if __name__ == "__main__":
    run_program()
