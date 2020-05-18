import pandas as pd

columns = ['date', 'ticker', 'transaction_type',
           'action', 'quantity', 'price',
           'share_balance', 'capital_gain']

pd.set_option('display.max_rows', None,
              'display.max_columns', None,
              'display.width', 1000)


def show_capgains_table(collection, tickers=None):
    global columns

    query = build_query(tickers)
    results_count = collection.count_documents(query)
    results = collection.find(query)

    if results_count == 0:
        print("No results found")

    else:
        df = pd.DataFrame([result for result in results]).sort_values('id')
        print(df[columns])


def build_query(tickers):
    query = dict()

    if tickers is not None and len(tickers) > 0:
        query['ticker'] = {"$in": tickers}

    return query
