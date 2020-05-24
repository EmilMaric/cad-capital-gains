from datetime import date, timedelta
from capgains.ticker_gains import TickerGains
import pytest


def test_ticker_gains_negative_balance(acb_transactions):
    with pytest.raises(ValueError):
        transactions = acb_transactions
        tg = TickerGains(transactions[2].ticker)
        tg.add_transaction(transactions[2], 1.2622)

def test_ticker_gains_ok(acb_transactions):
    transactions = acb_transactions
    tg = TickerGains(transactions[0].ticker)
    tg.add_transaction(transactions[0], 1.2507)
    assert transactions[0].share_balance == 21
    assert transactions[0].proceeds == -8088.477011999999
    assert transactions[0].capital_gain == 0.0
    assert transactions[0].acb_delta == 8088.477011999999
    assert transactions[0].acb == 8088.477011999999
    tg.add_transaction(transactions[1], 1.2622)
    assert transactions[1].share_balance == 63
    assert transactions[1].proceeds == -13234.545660000002
    assert transactions[1].capital_gain == 0.0
    assert transactions[1].acb_delta == 13234.545660000002
    assert transactions[1].acb == 21323.022672
    tg.add_transaction(transactions[2], 1.2622)
    assert transactions[2].share_balance == 43
    assert transactions[2].proceeds == 6260.120717999999
    assert transactions[2].capital_gain == -509.0928286666667
    assert transactions[2].acb_delta == -6769.213546666666
    assert transactions[2].acb == 14553.809125333333