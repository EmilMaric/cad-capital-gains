from datetime import date
import requests_mock as rm

import capgains.commands.capgains_calc as CapGainsCalc
from capgains.transaction import Transaction


def test_no_ticker(transactions, capfd, exchange_rates_mock):
    """Testing capgains_calc without any optional filters"""
    CapGainsCalc.capgains_calc(transactions, 2018)
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
[Total Gains = 6,970.00]
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |   share_balance |   proceeds |   capital_gain |   acb_delta |      acb |
|------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------|
| 2018-02-20 | RSU VEST           | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |              50 |  11,980.00 |       6,970.00 |   -5,010.00 | 5,010.00 |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+

GOOGL-2018
No capital gains

"""  # noqa: E501


def test_tickers(transactions, capfd, exchange_rates_mock):
    """Testing capgains_calc with a ticker"""
    CapGainsCalc.capgains_calc(transactions, 2018, ['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
[Total Gains = 6,970.00]
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |   share_balance |   proceeds |   capital_gain |   acb_delta |      acb |
|------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------|
| 2018-02-20 | RSU VEST           | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |              50 |  11,980.00 |       6,970.00 |   -5,010.00 | 5,010.00 |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+

"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_calc without any transactions"""
    CapGainsCalc.capgains_calc([], 2018)
    out, _ = capfd.readouterr()
    assert out == """\
No transactions available
"""


def test_unknown_year(transactions, capfd, exchange_rates_mock):
    """Testing capgains_calc with a year matching no transactions"""
    CapGainsCalc.capgains_calc(transactions, 1998)
    out, _ = capfd.readouterr()
    assert out == """\
ANET-1998
No capital gains

GOOGL-1998
No capital gains

"""


def test_superficial_loss_not_displayed(capfd, exchange_rates_mock):
    """Testing capgains_calc with a superficial loss transaction"""
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
            date(2018, 12, 1),
            'RSU VEST',
            'ANET',
            'SELL',
            1,
            1000.00,
            10.00,
            'USD'
        )
    ]
    CapGainsCalc.capgains_calc(transactions, 2018)
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
[Total Gains = -8,160.00]
+------------+--------------------+----------+----------+-------+----------+--------------+------------+-----------------+------------+----------------+-------------+-------+
| date       | transaction_type   | ticker   | action   |   qty |    price |   commission |   currency |   share_balance |   proceeds |   capital_gain |   acb_delta |   acb |
|------------+--------------------+----------+----------+-------+----------+--------------+------------+-----------------+------------+----------------+-------------+-------|
| 2018-12-01 | RSU VEST           | ANET     | SELL     |     1 | 1,000.00 |        10.00 |        USD |               0 |   1,980.00 |      -8,160.00 |  -10,140.00 |  0.00 |
+------------+--------------------+----------+----------+-------+----------+--------------+------------+-----------------+------------+----------------+-------------+-------+

"""  # noqa: E501


def test_calc_mixed_currencies(capfd, requests_mock):
    """testing capgains_calc with mixed currencies"""
    usd_transaction = Transaction(
            date(2017, 2, 15),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            50.00,
            0.00,
            'USD')
    cad_transaction = Transaction(
            date(2018, 2, 20),
            'RSU VEST',
            'ANET',
            'SELL',
            100,
            50.00,
            0.00,
            'CAD')
    transactions = [
        usd_transaction,
        cad_transaction
    ]

    usd_observations = [{
        'd': usd_transaction.date.isoformat(),
        'FXUSDCAD': {
            'v': '2.0'
        }
    }]
    requests_mock.get(rm.ANY, json={"observations": usd_observations})
    CapGainsCalc.capgains_calc(transactions, 2018)
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
[Total Gains = -5,000.00]
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+-------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |   share_balance |   proceeds |   capital_gain |   acb_delta |   acb |
|------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+-------|
| 2018-02-20 | RSU VEST           | ANET     | SELL     |   100 |   50.00 |         0.00 |        CAD |               0 |   5,000.00 |      -5,000.00 |  -10,000.00 |  0.00 |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+-------+

"""  # noqa: E501
