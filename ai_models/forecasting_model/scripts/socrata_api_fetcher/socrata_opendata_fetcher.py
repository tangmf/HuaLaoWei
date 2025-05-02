#!/usr/bin/env python3

"""
Socrata Open Data Fetcher with Pagination and Flexible SoQL Querying.

Required installations:
- pip install yaml
- pip install pandas
- pip install sodapy
"""

import os
import yaml
import pandas as pd
import time
from sodapy import Socrata
from typing import Optional, Dict
from requests.exceptions import ReadTimeout


def load_config_from_yaml(yaml_path: str, key: str) -> dict:
    with open(yaml_path, "r") as f:
        all_configs = yaml.safe_load(f)
    if key not in all_configs:
        raise KeyError(f"Configuration for '{key}' not found in {yaml_path}")
    return all_configs[key]

def fetch_socrata_data(
    domain: str,
    dataset_id: str,
    app_token: Optional[str] = None,
    limit_per_call: int = 1000,
    soql: Optional[Dict[str, str]] = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Fetches data from a Socrata Open Data API endpoint with flexible SoQL parameters.

    Args:
        domain (str): Socrata domain (e.g., "data.sfgov.org").
        dataset_id (str): Unique dataset identifier (e.g., "vw6y-z8j6").
        app_token (str): Optional app token for authentication.
        limit_per_call (int): Number of rows per request.
        soql (dict): Optional dict of SoQL query options: select, where, order, group.
        verbose (bool): If True, prints progress messages.

    Returns:
        pd.DataFrame: Combined result as a pandas DataFrame.
    """
    client = Socrata(domain, app_token, timeout=60) if app_token else Socrata(domain, None, timeout=60)

    offset = 0
    results_all = []

    # Extract SoQL clauses
    select = soql.get("select") if soql else None
    where = soql.get("where") if soql else None
    order = soql.get("order") if soql else None
    group = soql.get("group") if soql else None

    if verbose:
        print(f"Fetching from {domain}/{dataset_id}")
        print(f"SoQL query: where='{where}', order='{order}'")

    while True:
        if verbose:
            print(f"Fetching rows {offset + 1} to {offset + limit_per_call}...")

        for attempt in range(3):
            try:
                response = client.get(
                    dataset_id,
                    limit=limit_per_call,
                    offset=offset,
                    select=select,
                    where=where,
                    order=order,
                    group=group,
                )
                break
            except ReadTimeout:
                print(f"[Timeout] Attempt {attempt + 1}/3 at offset {offset}")
                time.sleep(5)
        else:
            raise RuntimeError("Failed to fetch data after 3 retry attempts.")

        if not response:
            if verbose:
                print("No more records returned by API.")
            break

        results_all.extend(response)
        offset += limit_per_call

    df = pd.DataFrame.from_records(results_all)
    if verbose:
        print(f"Total rows fetched: {len(df)}")
    return df


if __name__ == "__main__":
    config_key = "311_us_sanfrancisco"
    yaml_path = "config.yaml"

    config = load_config_from_yaml(yaml_path, config_key)

    df = fetch_socrata_data(
        domain=config["domain"],
        dataset_id=config["dataset_id"],
        app_token=config["app_token"],
        limit_per_call=config["limit_per_call"],
        soql=config["soql"]
    )

    os.makedirs(os.path.dirname(config["output_csv"]), exist_ok=True)
    df.to_csv(config["output_csv"], index=False)
    print(f"Saved to {config["output_csv"]}")
