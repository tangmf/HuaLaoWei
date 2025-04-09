#!/usr/bin/env python

# Required installations:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata
from datetime import datetime
import time
from requests.exceptions import ReadTimeout

def fetch_socrata_data(
    domain: str,
    dataset_id: str,
    limit_per_call: int = 1000,
    max_rows: int = 10000,
    app_token: str = None,
    date_column: str = None,
    start_date: str = None  # Format: "YYYY-MM-DD"
) -> pd.DataFrame:
    """
    Fetches data from a Socrata Open Data API endpoint with pagination and optional date filtering.

    Args:
        domain (str): The domain of the API (e.g., "data.sfgov.org").
        dataset_id (str): The dataset identifier (e.g., "vw6y-z8j6").
        limit_per_call (int): Number of rows per API call. Default is 1000.
        max_rows (int): Maximum number of rows to retrieve. Set to None to fetch all available rows.
        app_token (str): Optional Socrata app token.
        date_column (str): Name of the date field in the dataset (e.g., "created_date").
        start_date (str): ISO date string to filter from (e.g., "2022-04-07").

    Returns:
        pd.DataFrame: Combined DataFrame with all retrieved records.
    """
    client = Socrata(domain, app_token, timeout=60) if app_token else Socrata(domain, None, timeout=60)

    offset = 0
    all_results = []
    query_filter = ""

    if date_column and start_date:
        query_filter = f"{date_column} >= '{start_date}T00:00:00'"

    print(f"Fetching data from {domain}/{dataset_id}")
    print(f"Date filter: {query_filter or 'None'}")

    while True:
        print(f"Fetching rows {offset} to {offset + limit_per_call - 1}...")

        # Retry logic for timeouts
        retry_attempts = 3
        retry_delay = 5
        for attempt in range(retry_attempts):
            try:
                results = client.get(
                    dataset_id,
                    limit=limit_per_call,
                    offset=offset,
                    where=query_filter if query_filter else None,
                    order=f"{date_column} DESC" if date_column else None
                )
                break  # Exit retry loop if successful
            except ReadTimeout as e:
                print(f"Timeout at offset {offset}, attempt {attempt + 1}/{retry_attempts}")
                if attempt == retry_attempts - 1:
                    raise  # Raise exception after last attempt
                time.sleep(retry_delay)

        if not results:
            print("No more records returned by API.")
            break

        all_results.extend(results)
        offset += limit_per_call

        if max_rows is not None and offset >= max_rows:
            print("Reached maximum row limit.")
            break

    df = pd.DataFrame.from_records(all_results)
    print(f"Fetched {len(df)} rows.")
    return df


if __name__ == "__main__":
    country = "us"
    city = "chicago"
    domain = "data.cityofchicago.org"
    dataset_id = "v6vf-nfxy"
    date_column = "CREATED_DATE"  # Replace with correct date column name for each dataset
    start_date = (datetime.now().date().replace(year=datetime.now().year - 2)).isoformat()

    limit_per_call = 10000
    max_rows = 100000

    df = fetch_socrata_data(
        domain=domain,
        dataset_id=dataset_id,
        limit_per_call=limit_per_call,
        max_rows=max_rows,
        date_column=date_column,
        start_date=start_date
    )
    df.to_csv(f"./{country}/{city}_311.csv", index=False)
    print(f"Data saved to {city}_311_data.csv")


# https://data.sfgov.org/resource/vw6y-z8j6.json (requested_datetime)
# https://data.cityofchicago.org/resource/v6vf-nfxy.json (CREATED_DATE)
# https://data.cityofnewyork.us/resource/erm2-nwe9.json (created_date)
