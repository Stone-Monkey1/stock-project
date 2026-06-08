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
        contract_value = float(
            str(row["Award Amount"]).replace("$", "").replace(",", "")
        )

        # Calculate how many days ago this was awarded (simplified for example)
        # You would extract the real date from the API data here
        days_ago = 5

        # 3. Apply the time decay math
        time_multiplier = math.exp(-decay_rate * days_ago)

        # 4. Calculate the relative impact (Value / Market Cap)
        contract_score = (contract_value / market_cap) * time_multiplier

        total_score += contract_score

    # Factor in frequency (e.g., multiply by the number of contracts won)
    frequency_multiplier = len(company_contracts)
    final_score = total_score * frequency_multiplier

    return final_score
