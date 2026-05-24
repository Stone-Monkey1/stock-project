import requests

def get_dynamic_ticker_map():
  print("Downloading latest stock tickers from the SEC...")
  headers = {"User-Agent" : "AlecPowell (alecpow@gmail.com)"}
  sec_url = "https://www.sec.gov/files/company_tickers.json"

  response = requests.get(sec_url, headers=headers)
  if response.status_code != 200:
    print("Failed to fetch SEC data. Using empty dictionary.")
    return {}
  sec_data = response.json()
  dynamic_map = {}

  for entry in sec_data.values():
    company_name = entry["title"].upper()
    ticker = entry["ticker"]
    dynamic_map[company_name] = ticker

  print(f"Successfully loaded {len(dynamic_map)} public companies!")
  return dynamic_map
