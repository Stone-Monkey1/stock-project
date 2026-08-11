from scoring_toolbox.gov_tools import fetch_and_map_contracts
from scoring_toolbox.market_tools import get_market_cap
from scoring_toolbox.history_tools import load_scores, save_scores
from scoring_toolbox.scoring import calculate_daily_score, update_scoreboard
from scoring_toolbox.new_contract_bouncer import ensure_new_contract
import time


def run_program():
    print("Starting Quantitative Contract Tracker...")

    # 1. Load the historical contract lists from JSON
    # It will look like {"LMT": [...], "BA": [...]}
    historical_data = load_scores()

    # 2. Fetch today's new data
    contract_df = fetch_and_map_contracts()

    new_contracts = ensure_new_contract(contract_df)

    if new_contracts is None or new_contracts.empty:
        print("No new data to process today.")
        todays_scores = {}
        return

    else:

        unique_tickers = new_contracts["Ticker"].unique()
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
            company_new_contracts = new_contracts[new_contracts["Ticker"] == ticker]

            # Get their existing history from the JSON (or an empty list if they are new)
            daily_score = calculate_daily_score(company_new_contracts, market_cap)

            if daily_score > 0.0:
                todays_scores[ticker] = daily_score

            time.sleep(1)
    # 👉 Pass today's scores and the JSON history into the momentum mixer
    final_scoreboard = update_scoreboard(todays_scores, historical_data)

    # 4. Save the pruned historical data back to the hard drive
    save_scores(final_scoreboard)

    # 5. Print the Top 5 Categories
    print("\n🏆 --- TOP 5 DECAY SCORES --- 🏆")
    # This is already sorted by scoring.py, but we explicitly sort here just in case!
    top_decay = sorted(
        final_scoreboard.items(), key=lambda x: x[1]["decay_score"], reverse=True
    )[:5]
    for i, (ticker, data) in enumerate(top_decay):
        print(f"{i+1}. {ticker}: {data['decay_score']:.6f}")

    print("\n🚀 --- TOP 5 DELTA (DAILY JUMP) --- 🚀")
    # Re-sort the dictionary looking only at the "delta" key
    top_delta = sorted(
        final_scoreboard.items(), key=lambda x: x[1]["delta"], reverse=True
    )[:5]
    for i, (ticker, data) in enumerate(top_delta):
        # Notice the '+' in the formatting! It forces Python to show a + or - sign for momentum
        print(f"{i+1}. {ticker}: {data['delta']:+.6f}")

    print("\n📅 --- TOP 5 YTD SCORES --- 📅")
    # Re-sort the dictionary looking only at the "ytd_score" key
    top_ytd = sorted(
        final_scoreboard.items(), key=lambda x: x[1]["ytd_score"], reverse=True
    )[:5]
    for i, (ticker, data) in enumerate(top_ytd):
        # Added a comma format so large YTD numbers are easier to read (e.g., 1,500.23)
        print(f"{i+1}. {ticker}: {data['ytd_score']:,.6f}")


if __name__ == "__main__":
    run_program()
