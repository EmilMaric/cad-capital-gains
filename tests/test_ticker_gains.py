from capgains.ticker_gains import TickerGains
from capgains.exchange_rate import ExchangeRate
from click import ClickException
import pytest


def test_ticker_gains_negative_balance(transactions):
    """If the first transaction added is a sell, it is illegal since
    this causes a negative balance, which is impossible"""
    sell_transaction = transactions[2]
    tg = TickerGains(sell_transaction.ticker)
    er = ExchangeRate('USD', transactions[2].date, transactions[2].date)
    with pytest.raises(ClickException):
        tg.add_transactions([sell_transaction], er)


def test_ticker_gains_ok(transactions):
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date, transactions[3].date)

    # Add first transaction - 'BUY'
    # Add second transaction - 'BUY'
    # Add third transaction - 'SELL'
    transactions_to_test = [transactions[0],
                            transactions[2],
                            transactions[3]]
    
    tg.add_transactions(transactions_to_test, er)
    assert transactions[0].share_balance == 100
    assert transactions[0].proceeds == -10020.00
    assert transactions[0].capital_gain == 0.0
    assert transactions[0].acb_delta == 10020.00
    assert transactions[0].acb == 10020.00

    assert transactions[2].share_balance == 50
    assert transactions[2].proceeds == 11980.00
    assert transactions[2].capital_gain == 6970.00
    assert transactions[2].acb_delta == -5010.00
    assert transactions[2].acb == 5010.00

    assert transactions[3].share_balance == 100
    assert transactions[3].proceeds == -13020.00
    assert transactions[3].capital_gain == 0.0
    assert transactions[3].acb_delta == 13020.00
    assert transactions[3].acb == 18030.00
