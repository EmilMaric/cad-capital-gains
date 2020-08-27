from click import ClickException


class TickerGains:
    def __init__(self, ticker):
        self._ticker = ticker
        self._share_balance = 0
        self._total_acb = 0

    @property
    def ticker(self, ticker):
        return self._ticker

    def add_transaction(self, transaction, exchange_rate):
        """Adds a transaction and updates the calculated values."""
        new_share_balance = self._share_balance
        new_total_acb = self._total_acb
        if self._share_balance == 0:
            # to prevent divide by 0 error
            old_acb_per_share = 0
        else:
            old_acb_per_share = self._total_acb / self._share_balance
        if transaction.action == 'SELL':
            new_share_balance -= transaction.qty
            proceeds = (transaction.qty * transaction.price - transaction.commission) * exchange_rate  # noqa: E501
            capital_gain = proceeds - old_acb_per_share * transaction.qty
            acb_delta = -(old_acb_per_share * transaction.qty)
        else:
            new_share_balance += transaction.qty
            proceeds = -(transaction.qty * transaction.price - transaction.commission) * exchange_rate  # noqa: E501
            capital_gain = 0.0
            acb_delta = -proceeds
        new_total_acb += acb_delta
        if self._share_balance < 0:
            raise ClickException("Transaction caused negative share balance")
        transaction.share_balance = new_share_balance
        transaction.proceeds = proceeds
        transaction.capital_gain = capital_gain
        transaction.acb_delta = acb_delta
        transaction.acb = new_total_acb
        self._share_balance = new_share_balance
        self._total_acb = new_total_acb
