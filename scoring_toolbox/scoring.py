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
        old_decay = old_score["decay_score"]
        old_ytd = old_score["ytd_score"]
        if ticker in todays_scores_dict:

            new_decay = (old_decay * 0.985) + todays_scores_dict[ticker]
            # Then, use new_decay and old_decay to calculate your delta!
            # They won a contract today! Add it to their historical momentum.
            updated_scores[ticker] = {
                "decay_score": new_decay,
                "ytd_score": old_ytd + todays_scores_dict[ticker],
                "delta": new_decay - old_decay,
            }

        else:
            # They didn't win anything today. Decay their old score by 5%.
            new_decay = old_decay * 0.985
            updated_scores[ticker] = {
                "decay_score": old_decay * 0.985,
                "ytd_score": old_ytd,
                "delta": new_decay - old_decay,
            }

    # 2. Add brand new companies that just won their very first contract
    for ticker, new_score in todays_scores_dict.items():
        if ticker not in historical_scores_dict:
            updated_scores[ticker] = {
                "decay_score": new_score,
                "ytd_score": new_score,
                "delta": new_score,
            }

    # 3. Sort the dictionary from Highest Score to Lowest Score
    sorted_scores = dict(
        sorted(
            updated_scores.items(),
            key=lambda item: item[1]["decay_score"],
            reverse=True,
        )
    )

    return sorted_scores
