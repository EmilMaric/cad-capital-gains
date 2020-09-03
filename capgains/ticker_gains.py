from click import ClickException
from datetime import timedelta


class TickerGains:
    def __init__(self, ticker):
        self._ticker = ticker
        self._share_balance = 0
        self._total_acb = 0

    def add_transactions(self, transactions, exchange_rates):
        """Adds all transactions and updates the calculated values"""
        for transaction in transactions:
            rate = exchange_rates[transaction.currency] \
                    .get_rate(transaction.date)
            self._add_transaction(transaction, rate)
            transaction.superficial_loss = \
                self._is_superficial_loss(transaction, transactions)
            if transaction.superficial_loss:
                superficial_loss = transaction.capital_gain
                transaction.acb -= superficial_loss
                transaction.acb_delta -= superficial_loss
                transaction.capital_gain = 0
                self._total_acb -= superficial_loss

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

    def _add_transaction(self, transaction, exchange_rate):
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
            proceeds = -(transaction.qty * transaction.price + transaction.commission) * exchange_rate  # noqa: E501
            capital_gain = 0.0
            acb_delta = -proceeds
        new_total_acb += acb_delta
        if new_share_balance < 0:
            raise ClickException("Transaction caused negative share balance")
        transaction.share_balance = new_share_balance
        transaction.proceeds = proceeds
        transaction.capital_gain = capital_gain
        transaction.acb_delta = acb_delta
        transaction.acb = new_total_acb
        self._share_balance = new_share_balance
        self._total_acb = new_total_acb
