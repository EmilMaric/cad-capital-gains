from collections import OrderedDict


class Transaction:
    """Represents a transaction entry from the CSV-file"""
    date_idx = 0
    transaction_type_idx = 1
    ticker_idx = 2
    action_idx = 3
    qty_idx = 4
    price_idx = 5
    commission_idx = 6
    currency_idx = 7
    num_vals_show = 8
    num_vals_calculated = 5
    num_vals_all = num_vals_show + num_vals_calculated

    def __init__(self, date, transaction_type, ticker, action, qty, price,
                 commission, currency):
        self._date = date
        self._transaction_type = transaction_type
        self._ticker = ticker
        self._action = action
        self._qty = qty
        self._price = price
        self._commission = commission
        self._currency = currency
        self._share_balance = None
        self._proceeds = None
        self._capital_gain = None
        self._acb_delta = None
        self._acb = None
        self._superficial_loss = None

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

    @property
    def currency(self):
        return self._currency

    @property
    def share_balance(self):
        return self._share_balance

    @share_balance.setter
    def share_balance(self, share_balance):
        if(share_balance < 0):
            raise ValueError("Share balance cannot be negative")
        self._share_balance = share_balance

    @property
    def proceeds(self):
        return self._proceeds

    @proceeds.setter
    def proceeds(self, proceeds):
        self._proceeds = proceeds

    @property
    def capital_gain(self):
        return self._capital_gain

    @capital_gain.setter
    def capital_gain(self, capital_gain):
        self._capital_gain = capital_gain

    @property
    def acb_delta(self):
        return self._acb_delta

    @acb_delta.setter
    def acb_delta(self, acb_delta):
        self._acb_delta = acb_delta

    @property
    def acb(self):
        return self._acb

    @acb.setter
    def acb(self, acb):
        self._acb = acb

    @property
    def superficial_loss(self):
        return self._superficial_loss

    @superficial_loss.setter
    def superficial_loss(self, superficial_loss):
        self._superficial_loss = superficial_loss

    def to_dict(self, calculated_values=False):
        d = OrderedDict()
        d['date'] = self.date
        d['transaction_type'] = self.transaction_type
        d['ticker'] = self.ticker
        d['action'] = self.action
        d['qty'] = self.qty
        d['price'] = self.price
        d['commission'] = self.commission
        d['currency'] = self.currency
        if calculated_values:
            d['share_balance'] = self.share_balance
            d['proceeds'] = self.proceeds
            d['capital_gain'] = self.capital_gain
            d['acb_delta'] = self.acb_delta
            d['acb'] = self.acb
        return d
