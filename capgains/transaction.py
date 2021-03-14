class Transaction:
    """Represents a transaction entry from the CSV-file"""

    def __init__(self, date, description, ticker, action, qty, price,
                 commission, currency):
        self._date = date
        self._description = description
        self._ticker = ticker
        self._action = action
        self._qty = qty
        self._price = price
        self._commission = commission
        self._currency = currency
        self._exchange_rate = None
        self._share_balance = 0
        self._proceeds = 0.0
        self._capital_gain = 0.0
        self._acb = 0.0
        self._superficial_loss = False

    @property
    def date(self):
        return self._date

    @property
    def description(self):
        return self._description

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
    def exchange_rate(self):
        return self._exchange_rate

    @exchange_rate.setter
    def exchange_rate(self, exchange_rate):
        self._exchange_rate = exchange_rate

    @property
    def share_balance(self):
        return self._share_balance

    @share_balance.setter
    def share_balance(self, share_balance):
        if (share_balance < 0):
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

    @property
    def expenses(self):
        return self.commission * self.exchange_rate

    def set_superficial_loss(self):
        self.superficial_loss = True
        self.capital_gain = 0.0
