class Transactions:
    """Holds a collection of transactions"""

    def __init__(self, transactions):
        self._transactions = list()
        self._tickers = dict()
        for transaction in transactions:
            self.add_transaction(transaction)

    @property
    def transactions(self):
        """Return all the stored transactions"""
        return self._transactions

    @property
    def tickers(self):
        """Return all the unique tickers in this collection of transactions."""
        return sorted(self._tickers.keys())

    def __len__(self):
        return len(self.transactions)

    def __iter__(self):
        return iter(self.transactions)

    def __getitem__(self, x):
        return self.transactions[x]

    def add_transaction(self, transaction):
        """Add a transaction to the list of stored transactions."""
        self.transactions.append(transaction)

        ticker_refcount = self._tickers.get(transaction.ticker, 0)
        ticker_refcount += 1
        self._tickers[transaction.ticker] = ticker_refcount

    def filter_by(self, tickers=None, year=None, max_year=None, action=None,
                  superficial_loss=None):
        """Filter the list of stored transactions on certain parameters (such
        as ticker, year, etc) and return only the transactions that match the
        requested parameters.
        """
        def lambda_filter(t):
            keep = True
            if tickers:
                keep &= (t.ticker in tickers)
            if year:
                keep &= (t.date.year == year)
            if max_year:
                keep &= (t.date.year <= max_year)
            if action:
                keep &= (t.action == action)
            if superficial_loss is not None:
                # superficial_loss can be set to False, so need to explicitly
                # check that it is not set to None
                keep &= (t.superficial_loss == superficial_loss)
            return keep
        return Transactions(filter(lambda_filter, self.transactions))
