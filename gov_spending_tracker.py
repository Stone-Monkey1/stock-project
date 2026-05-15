# HTTP library for python
import requests
import pandas as pd

# This is an example of a dictionary, it has key : value pairs
TICKER_MAP = {
    "LOCKHEED MARTIN CORPORATION": "LMT",
    "THE BOEING COMPANY": "BA",
    "GENERAL DYNAMICS CORPORATION": "GD",
    "RAYTHEON COMPANY": "RTX",
    "NORTHROP GRUMMAN SYSTEMS CORPORATION": "NOC",
    "PFIZER INC.": "PFE",
    "MCKESSON CORPORATION": "MCK"
}
# how to define a function in python
# uses snake_case
# () holds potental arguments
# Doesn't use {} like JS or C# to group function/method content, python uses indentations
def fetch_and_map_contracts():
    print("Fetching recent data from USAspending.gov...")
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # This is a dictionary like above
    # However, this dictionary has arrays 

    payload = {
        "filters": {
            "award_type_codes" : ["A", "B", "C", "D"],
            "time_period": [{"start_date": "2024-04-01", "end_date": "2024-04-30"}]
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Funding Agency"],
        "limit": 100,
        "sort": "Award Amount",
        "order": "desc"
    }
    # Another dictionary
    headers = {"Content-Type": "application/json"}
    # does a post function on requests
    response = requests.post(url, json=payload, headers=headers)
    # Checks to see if the message received back from the HTTP address is giving the all clear
    # checking to see if connection is possible, it's acting basically like a boolean
    # is connected? true = if && false = else
    if response.status_code == 200:
        # response.json gets the raw text we get back from the website we posted to
        # .get is a built-in method for dictionaries
        # results and [] is what we're feeding to the get method
        # 'results' is the key wer're using looks inside the API response dictionary and grabs the data sitting inside the 'results' key
        # [] is the fallback value
        data = response.json().get('results', [])

        
        df = pd.DataFrame(data)
        
        # Makes the recipient names match ticker map format
        df['Recipient Name'] = df['Recipient Name'].str.upper()

        # THIS IS THE MISSING LINE: Maps the dictionary to create the 'Ticker' column
        df['Ticker'] = df['Recipient Name'].map(TICKER_MAP).fillna("Private/Unknown")

        # Now we can safely filter by it
        investable_df = df[df['Ticker'] != "Private/Unknown"].copy()

        print("\n--- Investable Public Contracts Found ---")

        if investable_df.empty:
            print("No matches in your date range. Try expanding your dictionary!")
        else:
            investable_df['Award Amount'] = investable_df['Award Amount'].apply(lambda x: f"${x:,.2f}")
            print(investable_df[['Ticker', 'Recipient Name', 'Award Amount', 'Funding Agency']].to_string(index=False))

    else:
        print(f"Failed to connect. Error code: {response.status_code}")

if __name__ == "__main__":
    fetch_and_map_contracts()