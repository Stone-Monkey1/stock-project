# HTTP library for python
import requests

# data analysis library
import pandas as pd

# Allows reference to current date and time
from datetime import datetime, timedelta

import time

# import ticker map function from adjacent file

from tools.sec_tools import get_dynamic_ticker_map, clean_company_name

# This is an example of a dictionary, it has key : value pairs
TICKER_MAP = get_dynamic_ticker_map()


# how to define a function in python
# uses snake_case
# () holds potental arguments
# Doesn't use {} like JS or C# to group function/method content, python uses indentations
def fetch_and_map_contracts():
    print("Fetching recent data from USAspending.gov...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # Get right now, then subtract exactly 1 day
    yesterday = datetime.now() - timedelta(days=180)
    today = datetime.now() - timedelta(days=175)

    # Format them into strings like "2024-05-18"
    start_date_str = yesterday.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")

    # This is a dictionary like above
    # However, this dictionary has arrays and even dictionaries within dictionaries
    # At this point we would need to look through the documention of the url to make sure the API can handle the payload we're sending.
    # The payload has specific values that correspond to the json dictionary that the url sends back
    payload = {
        "filters": {
            "award_type_codes": ["A", "B", "C", "D"],
            "time_period": [
                {
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "date_type": "last_modified_date",
                }
            ],
        },
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Funding Agency",
            "Description",
        ],
        "limit": 4,
        "sort": "Award Amount",
        "order": "desc",
    }
    # Another dictionary
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AlecPowell (alecpow@gmail.com)",
    }

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
        data = response.json().get("results", [])

        # Takes the data we just received from the response
        # pd is the shortened version of pandas
        # pandas is a data analysis library imported at the top
        # DataFrame is a function built into pandas
        # It basically creates a virtual excel spreadsheet that exists only in memory
        # pandas is fed data, looks at the keys within pandas and places the values underneath the keys
        # df is the created spreadsheet
        # df is standard
        df = pd.DataFrame(data)

        if df.empty:
            print("No contracts were found in the last 24 hours.")
            return
        print(
            f"Awesome! The API returned{len(df)} total contracts. Scanning for SEC matches..."
        )
        # Makes repient name all uppercase to match the format from TICKER_MAP
        # Heading already exists, so data is overwritten
        df["Recipient Name"] = df["Recipient Name"].str.upper()

        # .apply works as an in-line for loop, so for every row in "Recipent Name" it runs clean_company_name function

        df["Clean Name"] = df["Recipient Name"].apply(clean_company_name)

        # Creates a new column in the df spreadsheet
        # A new column is created because 'Ticker' isn't in the json data we got from the url
        # This is also from the API documentation. They don't care about stock tickers, so it isn't in the documention
        # Creates a new column in the df spreadsheet
        df["Ticker"] = df["Clean Name"].map(TICKER_MAP).fillna("PRIVATE / UNKNOWN")

        # --- REMOVE OR COMMENT OUT THIS LINE ---
        # investable_df = df[df["Ticker"] != "Private/Unknown"].copy()

        print("\n--- Top Government Contracts (Public & Private) ---")

        if df.empty:
            print("No matches in your date range.")
        else:
            # Format the Award Amount column to look like currency
            df["Award Amount"] = pd.to_numeric(
                df["Award Amount"], errors="coerce"
            ).fillna(0)

            df["Award Amount"] = df["Award Amount"].apply(lambda x: f"${x:,.2f}")

            df["Description"] = df["Description"].fillna("No description").astype(str)

            df["Description"] = df["Description"].apply(
                lambda x: x[:45] + "..." if len(x) > 45 else x
            )

            # Print the entire dataframe, showing both public and private!
            print(
                df[
                    [
                        "Ticker",
                        "Recipient Name",
                        "Award Amount",
                        "Description",
                        "Funding Agency",
                    ]
                ].to_string(index=False)
            )
            # ... (Your existing print statement for the dataframe is right above this) ...

            print("\n--- Digging into Private Contracts for Public Subcontractors ---")

            # Filter the spreadsheet down to just the private companies
            private_df = df[df["Ticker"] == "PRIVATE / UNKNOWN"]

            # Loop through the rows one by one
            for index, row in private_df.iterrows():
                award_id = str(row["Award ID"])
                prime_name = row["Recipient Name"]
                prime_amount = row["Award Amount"]

                print(f"Scanning {prime_name} for subcontracts... (ID: {award_id})")

                # Send the ID to our new scanner function
                subs = get_public_subcontractors(award_id, TICKER_MAP)

                # If we found public subcontractors, print them out!
                if subs:
                    print(f"\nPrime: {prime_name} ({prime_amount}) hired:")
                    for sub in subs:
                        print(sub)
                time.sleep(1)
    else:
        print(f"Failed to connect. Error code: {response.status_code}")


def get_public_subcontractors(award_id, ticker_map):
    # This is a docstring which displays helpful hints
    """Hits the reliable POST API to find who the prime contractor hired."""
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # We use the exact same reliable POST endpoint, but tell it we want subawards!
    payload = {
        "filters": {
            # Passes the award_id from feth_and_map_contracts
            "keywords": [award_id]
        },
        "subawards": True,
        "limit": 20,
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AlecPowell (alecpow@gmail.com)",
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return []

    sub_data = response.json().get("results", [])
    all_subs = []
    if not sub_data:
        return []

    for sub in sub_data:
        # APIs change keys frequently. We use fallbacks to guarantee we catch the data.
        sub_name = sub.get("Sub-Awardee Name") or sub.get("Recipient Name") or ""

        sub_amount = sub.get("Sub-Award Amount") or sub.get("Award Amount") or 0
        sub_amount = float(sub_amount)

        sub_name = str(sub_name).upper()
        clean_sub_name = clean_company_name(sub_name)

        # Check if this subcontractor is in our SEC dictionary
        ticker = ticker_map.get(clean_sub_name)

        if ticker:
            all_subs.append(
                f"   ↳ 📈 PUBLIC ({ticker}): {clean_sub_name} won a ${sub_amount:,.2f} subcontract"
            )
        else:
            all_subs.append(
                f"   ↳ 🏢 PRIVATE: {clean_sub_name} won a ${sub_amount:,.2f} subcontract"
            )

    return all_subs


if __name__ == "__main__":
    fetch_and_map_contracts()
