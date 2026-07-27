import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Alpaca SDK Imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Load environment keys
load_dotenv()
API_KEY = os.getenv("ALPACA_PAPER_API_KEY")
SECRET_KEY = os.getenv("ALPACA_PAPER_SECRET_KEY")

# Initialize Alpaca Clients (paper=True guarantees fake money!)
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)


def get_3_day_ago_price(ticker):
    """Fetches the closing price of a stock from roughly 3 days ago."""
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=5)  # 5 days to clear any weekends safely

    request_params = StockBarsRequest(
        symbol_or_symbols=ticker, timeframe=TimeFrame.Day, start=start_dt, end=end_dt
    )
    bars = data_client.get_stock_bars(request_params)

    # Extract the data list for this ticker
    ticker_bars = bars.data.get(ticker, [])
    if len(ticker_bars) >= 3:
        # Grab the close price from 3 trading bars ago
        return float(ticker_bars[-3].close)
    elif ticker_bars:
        return float(ticker_bars[0].close)
    return None


def run_trader():
    # --- Strategy Rules Configuration ---
    BUY_SCORE_THRESHOLD = 25.0
    STOP_LOSS_PCT = 0.08  # Rule 3: 8% Max Loss
    THREE_DAY_DROP_PCT = 0.10  # Rule 4: 10% drop over 3 days
    ALLOCATION_PER_TRADE = 1000  # Put $1000 into each stock we buy

    # Check available cash in the account (Rule 2)
    account = trading_client.get_account()
    available_cash = float(account.non_marginable_buying_power)

    # Load your current live portfolio positions
    current_positions = {pos.symbol: pos for pos in trading_client.get_all_positions()}

    # Load your quantitative scoreboard
    try:
        with open("historical_scores.json", "r") as file:
            scores = json.load(file)
    except FileNotFoundError:
        print("Error: historical_scores.json not found. Run main.py first.")
        return

    print(
        f"🤖 Starting Trade Execution Engine... (Available Cash: ${available_cash:,.2f})"
    )

    # ==========================================
    # PHASE 1: MANAGE EXISTING POSITIONS (SELL LOGIC)
    # ==========================================
    for ticker, position in current_positions.items():
        current_price = float(position.current_price)
        avg_entry_price = float(position.avg_entry_price)

        # Rule 3 Check: Has it dropped 8% below what we paid for it?
        unrealized_loss_pct = (avg_entry_price - current_price) / avg_entry_price
        if unrealized_loss_pct >= STOP_LOSS_PCT:
            print(
                f"🔴 SELL TRIGGERED (Stop Loss): {ticker} dropped {unrealized_loss_pct*100:.1f}% from entry price."
            )
            trading_client.close_position(ticker)
            continue  # Move to next position

        # Rule 4 Check: Has it dropped 10% or more over the last 3 days?
        three_days_ago_price = get_3_day_ago_price(ticker)
        if three_days_ago_price:
            three_day_drop = (
                three_days_ago_price - current_price
            ) / three_days_ago_price
            if three_day_drop >= THREE_DAY_DROP_PCT:
                print(
                    f"🔴 SELL TRIGGERED (3-Day Drop): {ticker} collapsed {three_day_drop*100:.1f}% over the last 3 days."
                )
                trading_client.close_position(ticker)
                continue

    # ==========================================
    # PHASE 2: EVALUATE NEW SIGNALS (BUY LOGIC)
    # ==========================================
    for ticker, score in scores.items():
        # Scale the decimal score by 1000 to match your "40" threshold target
        

        # Rule 1 Check: Score is high enough AND we don't already own it
        if score >= BUY_SCORE_THRESHOLD and ticker not in current_positions:

            # Rule 2 Check: Can we afford this trade?
            if available_cash >= ALLOCATION_PER_TRADE:
                print(
                    f"🟢 BUY TRIGGERED: {ticker} has an entry score of {score:.2f}!"
                )

                buy_order = MarketOrderRequest(
                    symbol=ticker,
                    notional=ALLOCATION_PER_TRADE,  # Orders exactly $1000 of shares
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                )
                trading_client.submit_order(order_data=buy_order)

                # Deduct from our tracking variable so we don't overspend on the next loop iteration
                available_cash -= ALLOCATION_PER_TRADE
            else:
                print(
                    f"⚠️ SKIPPED: Buy signal for {ticker} (Score: {score:.2f}) but insufficient cash."
                )

    print("🏁 Trade evaluation complete.")


if __name__ == "__main__":
    run_trader()
