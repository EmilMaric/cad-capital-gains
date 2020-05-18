from collections import OrderedDict


class Transaction:
    """Represents a transaction entry from the CSV-file"""
    num_vals = 7

    def __init__(self, date, transaction_type, ticker, action, qty, price,
                 commission):
        self._date = date
        self._transaction_type = transaction_type
        self._ticker = ticker
        self._action = action
        self._qty = qty
        self._price = price
        self._commission = commission

    @property
    def date(self):
        return self._date

    @property
    def transaction_type(self):
        return self._transaction_type

    @property
    def ticker(self):
        return self._ticker

    @property
    def action(self):
        return self._action

    @property
    def qty(self):
        return self._qty

    @property
    def price(self):
        return self._price

    @property
    def commission(self):
        return self._commission

    def to_dict(self):
        d = OrderedDict()
        d['date'] = self.date
        d['transaction_type'] = self.transaction_type
        d['ticker'] = self.ticker
        d['action'] = self.action
        d['qty'] = self.qty
        d['price'] = self.price
        d['commission'] = self.commission
        return d
