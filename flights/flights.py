import json
import pandas as pd
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from serpapi import GoogleSearch

PARAMS = {
  "api_key": "xxx",
  "engine": "google_flights",
  "hl": "en",
  "gl": "us",
  "departure_id": "HEL",
  "arrival_id": "JFK",
  "outbound_date": "",
  "return_date": "",
  "currency": "USD",
  "travel_class": "3",
  "show_hidden": "true"
}

def print_table(flights_json_files: list[str]) -> None:
    best_flights = []
    for flights_json_file in flights_json_files:        
        with open(flights_json_file, "r") as f:
            flights = json.load(f)
            best_flights.extend(flights.get('best_flights', []))
    flights_data = []
    for flight in best_flights:
        departure_time = flight['flights'][0]['departure_airport']['time']
        arrival_time = flight['flights'][len(flight['flights'])-1]['arrival_airport']['time']
        total_duration = flight['total_duration']
        airlines = ', '.join([flight['airline'] for flight in flight['flights']])
        price = flight['price']
        flights_data.append([departure_time, arrival_time, total_duration, airlines, price])
    df = pd.DataFrame(flights_data, columns=['Departure Time', 'Arrival Time', 'Total Duration', 'Airlines', 'Price'])
    df = df.sort_values(by='Price')
    df.to_csv("flights.tsv", index=False, sep="\t")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python flights.py <start_date>:<end_date> <start_date>:<end_date> api_key")
        sys.exit(1)
    PARAMS["api_key"] = sys.argv[3]
    # first and second argument are date range YYYY-MM-DD:YYYY-MM-DD
    date_ranges = []
    for i in [1, 2]:
        start_date_str, end_date_str = sys.argv[i].split(":")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        dates = [start_date + relativedelta(days=i) for i in range((end_date - start_date).days + 1)]
        date_ranges.append([date.strftime("%Y-%m-%d") for date in dates])

    out_filenames = []
    for dep in date_ranges[0]:
        for arr in date_ranges[1]:
            PARAMS["outbound_date"] = dep
            PARAMS["return_date"] = arr
            search = GoogleSearch(PARAMS)
            results = search.get_json()
            filename = f"{dep}_{arr}_results.json"
            out_filenames.append(filename)
            with open(filename, "w") as f:
                f.write(json.dumps(results, indent=4))

    print_table(out_filenames)
