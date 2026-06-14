import pandas as pd
import math
from datetime import datetime


def calculate_urgency_score(company_ticker, df, market_cap):
    """
    Calculates an investment urgency score for a specific public company.
    """
    company_contracts = df[df["Ticker"] == company_ticker]

    if company_contracts.empty:
        return 0.0

    total_score = 0.0
    decay_rate = 0.05  # Adjust this to make old contracts lose value faster or slower

    for index, row in company_contracts.iterrows():
        # Get the contract amount (ensure it's a float)
        contract_value = row["Amount"]

        # Calculate how many days ago this was awarded (simplified for example)
        # You would extract the real date from the API data here
        start_str = str(row["Start Date"])
        end_str = str(row["End Date"])

        if start_str == "None" or end_str == "None" or not start_str or not end_str:
            continue

        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")

        contract_duration_days = (end_date - start_date).days

        duration_years = contract_duration_days / 365.25

        duration_years = max(duration_years, 1.0)

        # 4. Calculate the relative impact (Value / Market Cap)
        contract_score = (contract_value / duration_years) / market_cap
        # print(contract_score)

        total_score += contract_score

    # Factor in frequency (e.g., multiply by the number of contracts won)
    frequency_multiplier = len(company_contracts)
    final_score = total_score * frequency_multiplier

    return final_score
