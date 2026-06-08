# Import your specific function from your custom api_tools.py file
from tools.gov_tools import fetch_and_map_contracts

# The steering wheel: this executes when you run main.py
if __name__ == "__main__":
    print("Starting Government Spending Tracker...")
    fetch_and_map_contracts()
    print("Process complete.") 

