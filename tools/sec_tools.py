import requests
import re

def clean_company_name(name):
  """Strips unnecessary words from company name to make it easier to map them"""

  name = str(name).upper()

  # Removes all hyphens, commas, periods etc from the name
  # the 'r' is raw string notation, it's used so python won't interfere with regex backslashes
  name = re.sub(r'[^\w\s]', '', name)

  suffixes = r'\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LLC|LP|LTD|THE)\b'

  name = re.sub(suffixes, '', name)

# Cleans any remining whitespaces and returns the name
  return " ".join(name.split())


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
    raw_name = entry["title"].upper()
    clean_name = clean_company_name(raw_name)
    ticker = entry["ticker"]

    dynamic_map[raw_name] = ticker

    if clean_name:
      dynamic_map[clean_name] = ticker

  print(f"Successfully loaded {len(dynamic_map)} public companies!")
  return dynamic_map
