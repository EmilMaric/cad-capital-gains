import pandas as pd

columns = ['date', 'ticker', 'transaction_type',
           'action', 'quantity', 'price',
           'share_balance', 'capital_gain']


def show_capgains_table(collection, tickers=None):
    global columns
    pd.set_option('display.max_rows', None,
                  'display.max_columns', None,
                  'display.width', 1000)

    query = build_query(tickers)
    results = collection.find(query)
    df = pd.DataFrame([result for result in results]).sort_values('id')
    print(df[columns])


def build_query(tickers):
    query = dict()
    if tickers is not None and len(tickers) > 0:
        query['tickers'] = {"$in": tickers}

    return query
