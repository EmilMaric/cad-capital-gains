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
    tg.add_transaction(transactions[0], 1.2507)
    assert transactions[0].share_balance == 21
    assert transactions[0].proceeds == -8062.224819
    assert transactions[0].capital_gain == 0.0
    assert transactions[0].acb_delta == 8062.224819
    assert transactions[0].acb == 8062.224819
    tg.add_transaction(transactions[1], 1.2622)
    assert transactions[1].share_balance == 63
    assert transactions[1].proceeds == -13229.24442
    assert transactions[1].capital_gain == 0.0
    assert transactions[1].acb_delta == 13229.24442
    assert transactions[1].acb == 21291.469239000002
    tg.add_transaction(transactions[2], 1.2622)
    assert transactions[2].share_balance == 43
    assert transactions[2].proceeds == 6260.120717999999
    assert transactions[2].capital_gain == -499.07586580952557
    assert transactions[2].acb_delta == -6759.196583809525
    assert transactions[2].acb == 14532.272655190478
