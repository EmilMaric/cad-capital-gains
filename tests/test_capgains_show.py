from capgains.commands import capgains_show as CapGainsShow
from capgains.transactions import Transactions


def test_no_filter(transactions, capfd):
    """Testing capgains_show without any filters"""
    CapGainsShow.capgains_show(transactions)
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
    """Testing capgains_show without any transactions"""
    CapGainsShow.capgains_show(Transactions([]))
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_ticker(transactions, capfd):
    """Testing capgains_show when providing a ticker filter"""
    CapGainsShow.capgains_show(transactions, tickers=['ANET'])
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
    transactions
    """
    CapGainsShow.capgains_show(transactions, tickers=['FB'])
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_known_ticker_and_unknown_ticker(transactions, capfd):
    """Testing capgains_show when providing a ticker not present in any
    transactions and a ticker that is present in a transaction
    """
    CapGainsShow.capgains_show(transactions, ['GOOGL', 'FB'])
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
    transactions
    """
    CapGainsShow.capgains_show(transactions, ['ANET', 'GOOGL'])
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
