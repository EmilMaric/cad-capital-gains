from datetime import date

from capgains.commands import capgains_show as CapGainsShow
from capgains.transaction import Transaction
from capgains.transactions import Transactions


def test_no_filter(transactions, capfd):
    """Testing capgains_show without any filters."""
    CapGainsShow.capgains_show(transactions, show_exchange_rate=False)
    out, _ = capfd.readouterr()
    assert out == """\
+------------+---------------+----------+----------+-------+---------+--------------+------------+
| date       | description   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+---------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE | ANET     | BUY      |   100 |   50.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST      | GOOGL    | BUY      |    30 |   20.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST      | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |
| 2019-02-15 | ESPP PURCHASE | ANET     | BUY      |    50 |  130.00 |        10.00 |        USD |
+------------+---------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_show without any transactions."""
    CapGainsShow.capgains_show(Transactions([]), show_exchange_rate=False)
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_ticker(transactions, capfd):
    """Testing capgains_show when providing a ticker filter."""
    CapGainsShow.capgains_show(
        transactions, show_exchange_rate=False, tickers=['ANET']
    )
    out, _ = capfd.readouterr()
    assert out == """\
+------------+---------------+----------+----------+-------+---------+--------------+------------+
| date       | description   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+---------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE | ANET     | BUY      |   100 |   50.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST      | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |
| 2019-02-15 | ESPP PURCHASE | ANET     | BUY      |    50 |  130.00 |        10.00 |        USD |
+------------+---------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501


def test_unknown_ticker(transactions, capfd):
    """Testing capgains_show when providing a ticker not present in any
    transactions."""
    CapGainsShow.capgains_show(
        transactions, show_exchange_rate=False, tickers=['FB']
    )
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_known_ticker_and_unknown_ticker(transactions, capfd):
    """Testing capgains_show when providing a ticker not present in any
    transactions and a ticker that is present in a transaction."""
    CapGainsShow.capgains_show(
        transactions, show_exchange_rate=False, tickers=['GOOGL', 'FB']
    )
    out, _ = capfd.readouterr()
    assert out == """\
+------------+---------------+----------+----------+-------+---------+--------------+------------+
| date       | description   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+---------------+----------+----------+-------+---------+--------------+------------|
| 2018-02-20 | RSU VEST      | GOOGL    | BUY      |    30 |   20.00 |        10.00 |        USD |
+------------+---------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501


def test_multiple_tickers(transactions, capfd):
    """Testing capgains_show when providing multiple tickers present in any
    transactions."""
    CapGainsShow.capgains_show(
        transactions, show_exchange_rate=False, tickers=['ANET', 'GOOGL']
    )
    out, _ = capfd.readouterr()
    assert out == """\
+------------+---------------+----------+----------+-------+---------+--------------+------------+
| date       | description   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+---------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE | ANET     | BUY      |   100 |   50.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST      | GOOGL    | BUY      |    30 |   20.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST      | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |
| 2019-02-15 | ESPP PURCHASE | ANET     | BUY      |    50 |  130.00 |        10.00 |        USD |
+------------+---------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501


def test_partial_shares(capfd, requests_mock):
    """Testing capgains_show with partial shares."""
    partial_buy = Transaction(
        date(2017, 2, 15),
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        0.5,
        50.00,
        0.00,
        'CAD'
    )
    partial_sell = Transaction(
        date(2018, 2, 20),
        'RSU VEST',
        'ANET',
        'SELL',
        0.5,
        100.00,
        0.00,
        'CAD'
    )
    transactions = Transactions([partial_buy, partial_sell])

    CapGainsShow.capgains_show(
        transactions, show_exchange_rate=False, tickers=['ANET']
    )
    out, _ = capfd.readouterr()
    assert out == """\
+------------+---------------+----------+----------+-------+---------+--------------+------------+
| date       | description   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+---------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE | ANET     | BUY      |   0.5 |   50.00 |         0.00 |        CAD |
| 2018-02-20 | RSU VEST      | ANET     | SELL     |   0.5 |  100.00 |         0.00 |        CAD |
+------------+---------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501
