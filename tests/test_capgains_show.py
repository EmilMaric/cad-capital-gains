import capgains.commands.capgains_show as CapGainsShow
from datetime import datetime as dt
import pytest

from capgains.transaction import Transaction


@pytest.fixture(scope='module')
def transactions():
    trans = [
        Transaction(
            dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            '21',
            '307.96',
            '20.99',
        ),
        Transaction(
            dt.strftime(dt(2018, 2, 20), '%Y-%m-%d'),
            'RSU VEST',
            'GOOGL',
            'BUY',
            '42',
            '249.55',
            '0.00',
        ),
    ]
    return trans


def test_no_filter(transactions, capfd):
    CapGainsShow.capgains_show(transactions)
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501


def test_no_transactions(capfd):
    CapGainsShow.capgains_show([])
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_ticker(transactions, capfd):
    CapGainsShow.capgains_show(transactions, tickers=['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
"""  # noqa: E501


def test_unknown_ticker(transactions, capfd):
    CapGainsShow.capgains_show(transactions, tickers=['FB'])
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_known_ticker_and_unknown_ticker(transactions, capfd):
    CapGainsShow.capgains_show(transactions, ['GOOGL', 'FB'])
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501


def test_multiple_tickers(transactions, capfd):
    CapGainsShow.capgains_show(transactions, ['ANET', 'GOOGL'])
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501
