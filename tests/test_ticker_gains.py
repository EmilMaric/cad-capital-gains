from click import ClickException
import pytest
from datetime import date

from capgains.ticker_gains import TickerGains
from capgains.exchange_rate import ExchangeRate
from capgains.transaction import Transaction


def test_superficial_loss_no_purchase_after_loss(exchange_rates_mock):
    """Testing if transaction is marked as a superficial loss even if
    there are no purchases made after the loss"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            100.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 1, 2),
            'RSU VEST',
            'ANET',
            'SELL',
            99,
            50.00,
            10.00,
            'USD'
        )
    ]
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date,
                      transactions[1].date)
    er_map = {'USD': er}
    tg.add_transactions(transactions, er_map)
    assert transactions[1].superficial_loss
    assert transactions[1].capital_gain == 0


def test_superficial_loss_purchase_after_loss(exchange_rates_mock):
    """Testing if transaction is marked as a superficial loss even if
    there is a purchase made after the loss"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            100.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 1, 2),
            'RSU VEST',
            'ANET',
            'SELL',
            99,
            50.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 1, 3),
            'RSU VEST',
            'ANET',
            'BUY',
            1,
            100.00,
            10.00,
            'USD'
        )
    ]
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date,
                      transactions[1].date)
    er_map = {'USD': er}
    tg.add_transactions(transactions, er_map)
    assert transactions[1].superficial_loss
    assert transactions[1].capital_gain == 0


def test_loss_no_balance_after_window(exchange_rates_mock):
    """Testing if transaction is not marked as a superficial loss if
    there are is no share balance 30 days after the loss"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            100.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 1, 2),
            'RSU VEST',
            'ANET',
            'SELL',
            99,
            50.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 1, 3),
            'RSU VEST',
            'ANET',
            'SELL',
            1,
            100.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 2, 10),
            'RSU VEST',
            'ANET',
            'BUY',
            1,
            100.00,
            10.00,
            'USD'
        )
    ]
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date,
                      transactions[1].date)
    er_map = {'USD': er}
    tg.add_transactions(transactions, er_map)
    assert not transactions[1].superficial_loss
    assert transactions[1].capital_gain < 0


def test_loss_no_purchase_in_window(exchange_rates_mock):
    """Testing if transaction is not marked as a superficial loss if
    there are are no purchases made in the 61 day window"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            100.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 8, 1),
            'RSU VEST',
            'ANET',
            'SELL',
            99,
            50.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 12, 1),
            'RSU VEST',
            'ANET',
            'BUY',
            1,
            50.00,
            10.00,
            'USD'
        )
    ]
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date,
                      transactions[1].date)
    er_map = {'USD': er}
    tg.add_transactions(transactions, er_map)
    assert not transactions[1].superficial_loss
    assert transactions[1].capital_gain < 0


def test_gain_not_marked_as_superficial_loss(exchange_rates_mock):
    """Testing if transaction is not marked as a superficial loss if
    it does not result in a loss"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            1.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 8, 1),
            'RSU VEST',
            'ANET',
            'SELL',
            100,
            50.00,
            10.00,
            'USD'
        )
    ]
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date,
                      transactions[1].date)
    er_map = {'USD': er}
    tg.add_transactions(transactions, er_map)
    assert not transactions[1].superficial_loss
    assert transactions[1].capital_gain > 0


def test_ticker_gains_negative_balance(transactions, exchange_rates_mock):
    """If the first transaction added is a sell, it is illegal since
    this causes a negative balance, which is impossible"""
    sell_transaction = transactions[2]
    tg = TickerGains(sell_transaction.ticker)
    er = ExchangeRate('USD', transactions[2].date, transactions[2].date)
    er_map = {'USD': er}
    with pytest.raises(ClickException):
        tg.add_transactions([sell_transaction], er_map)


def test_ticker_gains_ok(transactions, exchange_rates_mock):
    tg = TickerGains(transactions[0].ticker)
    er = ExchangeRate('USD', transactions[0].date, transactions[3].date)
    er_map = {'USD': er}

    # Add first transaction - 'BUY'
    # Add second transaction - 'BUY'
    # Add third transaction - 'SELL'
    transactions_to_test = [transactions[0],
                            transactions[2],
                            transactions[3]]

    tg.add_transactions(transactions_to_test, er_map)
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
