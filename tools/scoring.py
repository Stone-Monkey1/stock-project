def calculate_daily_score(company_new_contracts, market_cap):
    """
    Calculates the base urgency score for a single day's worth of contracts.
    Formula: (Sum of Today's Contracts) / Market Cap
    """
    if market_cap == 0.0 or company_new_contracts.empty:
        return 0.0

    # Sum up all the contract amounts won today
    daily_revenue_sum = company_new_contracts["Amount"].sum()

    # Divide by market cap
    score = (daily_revenue_sum / market_cap) * 100
    return score


def update_scoreboard(todays_scores_dict, historical_scores_dict):
    """
    Applies new scores to the scoreboard, applies a 5% decay to companies
    that didn't win anything, and sorts the final list in descending order.
    """
    updated_scores = {}

    # 1. Update existing companies and apply the 5% decay to the losers
    for ticker, old_score in historical_scores_dict.items():
        if ticker in todays_scores_dict:
            # They won a contract today! Add it to their historical momentum.
            updated_scores[ticker] = old_score + todays_scores_dict[ticker]
        else:
            # They didn't win anything today. Decay their old score by 5%.
            updated_scores[ticker] = old_score * 0.985

    # 2. Add brand new companies that just won their very first contract
    for ticker, new_score in todays_scores_dict.items():
        if ticker not in historical_scores_dict:
            updated_scores[ticker] = new_score

    # 3. Sort the dictionary from Highest Score to Lowest Score
    sorted_scores = dict(
        sorted(updated_scores.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_scores
