# HTTP library for python
import requests
# data analysis library
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
    # However, this dictionary has arrays and even dictionaries within dictionaries
     # At this point we would need to look through the documention of the url to make sure the API can handle the payload we're sending.
    # The payload has specific values that correspond to the json dictionary that the url sends back
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


        # Takes the data we just received from the response
        # pd is the shortened version of pandas
        # pandas is a data analysis library imported at the top
        # DataFrame is a function built into pandas
        # It basically creates a virtual excel spreadsheet that exists only in memory
        # pandas is fed data, looks at the keys within pandas and places the values underneath the keys
        # df is the created spreadsheet
        # df is standard
        
        df = pd.DataFrame(data)
        
        # Makes repient name all uppercase to match the format from TICKER_MAP
        # Heading already exists, so data is overwritten
        df['Recipient Name'] = df['Recipient Name'].str.upper()

        # Creates a new column in the df spreadsheet
        # A new column is created because 'Ticker' isn't in the json data we got from the url
        # This is also from the API documentation. They don't care about stock tickers, so it isn't in the documention
        df['Ticker'] = df['Recipient Name'].map(TICKER_MAP).fillna("Private/Unknown")

        # Grabs the rows that have ticker values that aren't equal to "Private/Unknown"
        # copy() is a pandas best practice
        # this creates a new spreadsheet that's a copy of df with just the rows rows that have ticker values that aren't equal to "Private/Unknown"
        investable_df = df[df['Ticker'] != "Private/Unknown"].copy()

        print("\n--- Investable Public Contracts Found ---")

        if investable_df.empty:
            print("No matches in your date range. Try expanding your dictionary!")
        else:
            # .apply sets up an assembly line
            # It runs the following function on every cell within investable_df
            # lambda is a keyword to create a one line throw. away function
            # lambda x: means to creates a small function where x represents the current number we've looking at in the assembly line
            # f is a format string it turns a raw number into a currency format
            # f warns Python to expect a function {} within the ""
            # x is the raw number in the table
            # ,.2f the , tells python to add commas to the thousands place .2f forces two decimal places
            
            investable_df['Award Amount'] = investable_df['Award Amount'].apply(lambda x: f"${x:,.2f}")
            print(investable_df[['Ticker', 'Recipient Name', 'Award Amount', 'Funding Agency']].to_string(index=False))

    else:
        print(f"Failed to connect. Error code: {response.status_code}")

if __name__ == "__main__":
    fetch_and_map_contracts()