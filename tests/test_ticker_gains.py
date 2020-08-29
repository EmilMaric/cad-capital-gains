from capgains.ticker_gains import TickerGains
import pytest


def test_ticker_gains_negative_balance(transactions):
    """If the first transaction added is a sell, it is illegal since
    this causes a negative balance, which is impossible"""
    sell_transaction = transactions[2]
    tg = TickerGains(sell_transaction.ticker)
    with pytest.raises(ValueError):
        tg.add_transaction(sell_transaction, 1.2622)


def test_ticker_gains_ok(transactions):
    tg = TickerGains(transactions[0].ticker)

    # Add first transaction - 'BUY'
    tg.add_transaction(transactions[0], 2.0)
    assert transactions[0].share_balance == 100
    assert transactions[0].proceeds == -10020.00
    assert transactions[0].capital_gain == 0.0
    assert transactions[0].acb_delta == 10020.00
    assert transactions[0].acb == 10020.00

    # Add second transaction - 'BUY'
    tg.add_transaction(transactions[2], 2.0)
    assert transactions[2].share_balance == 50
    assert transactions[2].proceeds == 11980.00
    assert transactions[2].capital_gain == 6970.00
    assert transactions[2].acb_delta == -5010.00
    assert transactions[2].acb == 5010.00

    # Add third transaction - 'SELL'
    tg.add_transaction(transactions[3], 2.0)
    assert transactions[3].share_balance == 100
    assert transactions[3].proceeds == -13020.00
    assert transactions[3].capital_gain == 0.0
    assert transactions[3].acb_delta == 13020.00
    assert transactions[3].acb == 18030.00
