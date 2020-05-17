import pandas as pd


def show_capgains_table(collection, tickers=None):
    query = build_query(tickers)
    results = collection.find(query)
    columns = ['date', 'quantity', 'price', 'ticker']
    df = pd.DataFrame([result for result in results]).sort_values('id')
    print(df[columns])


def build_query(tickers):
    query = dict()
    if tickers is not None and len(tickers) > 0:
        query['tickers'] = {"$in": tickers}

    return query
