import pandas as pd
import csv
import os


columns = ['date', 'ticker', 'transaction_type',
           'action', 'quantity', 'price',
           'share_balance', 'capital_gain']

pd.set_option('display.max_rows', None,
              'display.max_columns', None,
              'display.width', 1000)


def show_capgains_table(filepath, tickers=None):
    if not os.path.isfile(filepath):
        print("File does not exist")
        return

    # open csv file and load data into list of dicts (each row is a dict)
    with open(filepath) as csv_file:
        data = [{key: value for key, value in row.items()}
                for row in csv.DictReader(csv_file)]

        print_data(data, tickers)


def print_data(data, tickers=None):
    global columns

    results = filter_data(data, tickers)

    if len(results) == 0:
        print("No results found")

    else:
        df = pd.DataFrame([result for result in results]).sort_values('id')
        print(df[columns])


def filter_data(data, tickers):
    res = data

    if tickers is not None and len(tickers) > 0:
        res = list(filter(lambda d: d['ticker'] in tickers, data))

    return res
