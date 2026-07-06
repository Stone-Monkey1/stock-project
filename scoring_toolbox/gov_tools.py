# HTTP library for python
import requests

# data analysis library
import pandas as pd

# Allows reference to current date and time
from datetime import datetime, timedelta
import time

# import ticker map function from adjacent file
from scoring_toolbox.sec_tools import get_dynamic_ticker_map, clean_company_name

# This is an example of a dictionary, it has key : value pairs
TICKER_MAP = get_dynamic_ticker_map()


def fetch_and_map_contracts():
    print("Fetching recent data from USAspending.gov...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # 1. Switch back to the 1-day daily sweep!
    days_to_sweep = 2

    start_date = datetime.now() - timedelta(days=days_to_sweep)
    end_date = datetime.now()

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    all_raw_data = []

    # 2. Setup the exhaustive loop variables
    page_num = 1
    has_next_page = True

    # 3. Keep looping until the API says there are no more pages
    while has_next_page:
        print(f"Fetching Page {page_num} of the {days_to_sweep}-Day Sweep...")

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
                "Start Date",
                "End Date",
            ],
            "limit": 100,
            "page": page_num,
            "sort": "Award Amount",
            "order": "desc",
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AlecPowell (alecpow@gmail.com)",
        }

        # --- NEW RETRY SHIELD FOR PRIMES ---
        max_retries = 3
        success = False

        for attempt in range(max_retries):
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                success = True
                break  # We got the data! Break out of the retry loop.
            else:
                print(
                    f"⚠️ API hiccup on Page {page_num} (Error {response.status_code}). Retrying in 5 seconds... (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(15)  # Wait 5 seconds to let their server recover

        # If we failed all 3 attempts, break the main pagination loop
        if not success:
            print(
                f"🚨 Failed to connect on Page {page_num} after {max_retries} attempts. Stopping pagination."
            )
            break
        # -----------------------------------

        data_dict = response.json()

        # Extract the contracts
        page_data = data_dict.get("results", [])
        all_raw_data.extend(page_data)

        # Check the API's metadata to see if we need to turn the page again!
        page_metadata = data_dict.get("page_metadata", {})
        has_next_page = page_metadata.get("hasNext", False)

        page_num += 1

        # CRITICAL: Pause for 1 second so the government doesn't ban your IP!
        time.sleep(1)

    # Once all pages are collected, turn the massive list into our Pandas Spreadsheet!
    if not all_raw_data:
        print("No contracts were found in the selected date range.")
        return pd.DataFrame()

    df = pd.DataFrame(all_raw_data)

    if df.empty:
        print("No contracts were found in the last 24 hours.")
        return pd.DataFrame()

    print(
        f"Awesome! The API returned {len(df)} total contracts. Scanning for SEC matches..."
    )

    # Makes repient name all uppercase to match the format from TICKER_MAP
    df["Recipient Name"] = df["Recipient Name"].str.upper()

    # .apply works as an in-line for loop, so for every row in "Recipent Name" it runs clean_company_name function
    df["Clean Name"] = df["Recipient Name"].apply(clean_company_name)

    # Creates a new column in the df spreadsheet
    df["Ticker"] = df["Clean Name"].map(TICKER_MAP).fillna("PRIVATE / UNKNOWN")

    print("\n--- Top Government Contracts (Public & Private) ---")

    # Format the Award Amount column to look like currency
    df["Raw Amount"] = pd.to_numeric(df["Award Amount"], errors="coerce").fillna(0)
    df["Award Amount"] = df["Raw Amount"].apply(lambda x: f"${x:,.2f}")

    df["Description"] = df["Description"].fillna("No description").astype(str)
    df["Description"] = df["Description"].apply(
        lambda x: x[:45] + "..." if len(x) > 45 else x
    )

    print("\n--- Compiling Public Primes and Subcontracts for Scoring ---")

    master_contract_list = []

    # FUNNEL 1: Grab ALL public prime contracts (No minimum amount! We want every penny)
    public_primes = df[df["Ticker"] != "PRIVATE / UNKNOWN"]

    for index, row in public_primes.iterrows():
        master_contract_list.append(
            {
                "Award ID": str(row["Award ID"]),
                "Ticker": row["Ticker"],
                "Company Name": row["Clean Name"],
                "Amount": row["Raw Amount"],
                "Type": "Prime Contract",
                "Start Date": row["Start Date"],
                "End Date": row["End Date"],
            }
        )

    # FUNNEL 2: Grab ALL large prime contracts to scan for subawards
    # This protects your API from scanning thousands of tiny, irrelevant contracts
    big_prime_contracts = df[df["Raw Amount"] >= 500000]

    total_to_scan = len(big_prime_contracts)
    print(f"🔍 Scanning {total_to_scan} large prime contracts for sub-awards...")

    for count, (index, row) in enumerate(big_prime_contracts.iterrows(), 1):
        short_award_id = str(row["Award ID"])
        prime_start = row["Start Date"]
        prime_end = row["End Date"]

        if count % 50 == 0:
            print(f"   ... scanned {count} out of {total_to_scan} ...")

        # Send the ID to our scanner function
        subs = get_public_subcontractors(
            short_award_id, TICKER_MAP, prime_start, prime_end
        )

        # If we found public subcontractors, add them to our master list!
        if subs:
            master_contract_list.extend(subs)
        time.sleep(1)

    # Convert the final list into a DataFrame and return it to main.py
    final_df = pd.DataFrame(master_contract_list)
    return final_df


def get_public_subcontractors(short_award_id, ticker_map, prime_start, prime_end):
    """Hits the reliable POST API to find who the prime contractor hired."""

    url = "https://api.usaspending.gov/api/v2/subawards/"

    payload = {
        "filters": {
            "award_id": [short_award_id],
        },
        "subawards": True,
        "limit": 100,
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AlecPowell (alecpow@gmail.com)",
    }

    # --- NEW RETRY SHIELD FOR SUBCONTRACTS ---
    max_retries = 3
    success = False

    for attempt in range(max_retries):
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            success = True
            break
        else:
            # We don't want to print every failure here since it runs hundreds of times,
            # but we will wait 5 seconds before trying again
            time.sleep(15)

    if not success:
        return []
    # -----------------------------------------

    sub_data = response.json().get("results", [])
    all_subs = []

    if not sub_data:
        return []

    for sub in sub_data:
        sub_name = sub.get("Sub-Awardee Name") or sub.get("recipient_name") or ""
        sub_id = str(sub.get("subaward_number"))

        sub_amount = sub.get("Sub-Award Amount") or sub.get("amount") or 0
        sub_amount = float(sub_amount)

        sub_name = str(sub_name).upper()
        clean_sub_name = clean_company_name(sub_name)

        ticker = ticker_map.get(clean_sub_name)

        if ticker:
            all_subs.append(
                {
                    "Award ID": sub_id,
                    "Ticker": ticker,
                    "Company Name": clean_sub_name,
                    "Amount": sub_amount,
                    "Type": "Subcontract",
                    "Start Date": prime_start,
                    "End Date": prime_end,
                }
            )

    return all_subs


if __name__ == "__main__":
    fetch_and_map_contracts()
