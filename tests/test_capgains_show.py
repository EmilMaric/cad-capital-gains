import capgains.commands.capgains_show as CapGainsShow


def test_no_filter(transactions, capfd):
    """Testing capgains_show without any filters"""
    CapGainsShow.capgains_show(transactions)
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_show without any transactions"""
    CapGainsShow.capgains_show([])
    out, _ = capfd.readouterr()
    assert out == """\
No results found
"""


def test_ticker(transactions, capfd):
    """Testing capgains_show when providing a ticker filter"""
    CapGainsShow.capgains_show(transactions, tickers=['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
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
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501


def test_multiple_tickers(transactions, capfd):
    """Testing capgains_show when providing multiple tickers present in any
    transactions
    """
    CapGainsShow.capgains_show(transactions, ['ANET', 'GOOGL'])
    out, _ = capfd.readouterr()
    assert out == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501
