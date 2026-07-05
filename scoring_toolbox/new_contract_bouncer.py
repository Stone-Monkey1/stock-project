import json
import os
import pandas as pd
from datetime import datetime, timedelta

LEDGER_FILE = "seen_award_ids.json"


def ensure_new_contract(contract_df):
    """
    Docstring for ensure_new_contract

    :param contract_df: Description
    filters out already seen contracts, and purges old contracts
    """
    if contract_df is None or contract_df.empty:
        return contract_df

    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as file:
            seen_ledger = json.load(file)
    else:
        seen_ledger = {}

    is_new = ~contract_df["Award ID"].isin(seen_ledger.keys())
    new_contracts_df = contract_df[is_new].copy()

    today_str = datetime.now().strftime("%Y-%m-%d")

    for award_id in new_contracts_df["Award ID"]:
        seen_ledger[award_id] = today_str

    seven_days_ago = datetime.now() - timedelta(days=7)
    pruned_ledger = {}

    for award_id, date_seen_str in seen_ledger.items():
        date_seen_obj = datetime.strptime(date_seen_str, "%Y-%m-%d")

        if date_seen_obj >= seven_days_ago:
            pruned_ledger[award_id] = date_seen_str
    with open(LEDGER_FILE, "w") as file:
        json.dump(pruned_ledger, file, indent=4)

    return new_contracts_df
