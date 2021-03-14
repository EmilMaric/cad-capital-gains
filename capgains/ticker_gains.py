from click import ClickException
from datetime import timedelta


class TickerGains:
    def __init__(self, ticker):
        self._ticker = ticker
        self._share_balance = 0
        self._total_acb = 0

    def add_transactions(self, transactions, exchange_rates):
        """Adds all transactions and updates the calculated values"""
        for t in transactions:
            rate = exchange_rates[t.currency].get_rate(t.date)
            t.exchange_rate = rate
            self._add_transaction(t)
            if self._is_superficial_loss(t, transactions):
                self._total_acb -= t.capital_gain
                t.set_superficial_loss()

    def _superficial_window_filter(self, transaction, min_date, max_date):
        """Filter out BUY transactions that fall within
        the 61 day superficial loss window"""
        return transaction.date >= min_date and transaction.date <= max_date

    def _is_superficial_loss(self, transaction, transactions):
        """Figures out if the transaction is a superficial loss"""
        # Has to be a capital loss
        if (transaction.capital_gain >= 0):
            return False
        min_date = transaction.date - timedelta(days=30)
        max_date = transaction.date + timedelta(days=30)
        filtered_transactions = list(filter(
            lambda t: self._superficial_window_filter(t, min_date, max_date),
            transactions))
        # Has to have a purchase either 30 days before or 30 days after
        if (not any(t.action == 'BUY' for t in filtered_transactions)):
            return False
        # Has to have a positive share balance after 30 days
        transaction_idx = filtered_transactions.index(transaction)
        balance = transaction._share_balance
        for window_transaction in filtered_transactions[transaction_idx+1:]:
            if window_transaction.action == 'SELL':
                balance -= window_transaction.qty
            else:
                balance += window_transaction.qty
        return balance > 0

    def _add_transaction(self, transaction):
        """Adds a transaction and updates the calculated values."""
        if self._share_balance == 0:
            # to prevent divide by 0 error
            old_acb_per_share = 0
        else:
            old_acb_per_share = self._total_acb / self._share_balance
        proceeds = (transaction.qty * transaction.price) * transaction.exchange_rate  # noqa: E501
        if transaction.action == 'SELL':
            self._share_balance -= transaction.qty
            acb = old_acb_per_share * transaction.qty
            capital_gain = proceeds - transaction.expenses - acb
            self._total_acb -= acb
        else:
            self._share_balance += transaction.qty
            acb = proceeds + transaction.expenses
            capital_gain = 0.0
            self._total_acb += acb
        if self._share_balance < 0:
            raise ClickException("Transaction caused negative share balance")
        transaction.share_balance = self._share_balance
        transaction.proceeds = proceeds
        transaction.capital_gain = capital_gain
        transaction.acb = acb
