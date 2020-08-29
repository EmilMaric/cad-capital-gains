import capgains.commands.capgains_calc as CapGainsCalc


def test_no_ticker(transactions, capfd, exchange_rates_mock):
    """Testing capgains_calc without any optional filters"""
    CapGainsCalc.capgains_calc(transactions, 2018)
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
date        transaction_type    ticker    action      qty    price    commission    share_balance    proceeds    capital_gain    acb_delta       acb
----------  ------------------  --------  --------  -----  -------  ------------  ---------------  ----------  --------------  -----------  --------
2018-02-20  RSU VEST            ANET      SELL         50   120.00         10.00               50   11,980.00        6,970.00    -5,010.00  5,010.00

GOOGL-2018
No capital gains

"""  # noqa: E501


def test_tickers(transactions, capfd, exchange_rates_mock):
    """Testing capgains_calc with a ticker"""
    CapGainsCalc.capgains_calc(transactions, 2018, ['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
date        transaction_type    ticker    action      qty    price    commission    share_balance    proceeds    capital_gain    acb_delta       acb
----------  ------------------  --------  --------  -----  -------  ------------  ---------------  ----------  --------------  -----------  --------
2018-02-20  RSU VEST            ANET      SELL         50   120.00         10.00               50   11,980.00        6,970.00    -5,010.00  5,010.00

"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_show without any transactions"""
    CapGainsCalc.capgains_calc([], 2018)
    out, _ = capfd.readouterr()
    assert out == """\
No transactions available
"""


def test_unknown_year(transactions, capfd, exchange_rates_mock):
    """Testing capgains_show with a year matching no transactions"""
    CapGainsCalc.capgains_calc(transactions, 1998)
    out, _ = capfd.readouterr()
    assert out == """\
ANET-1998
No capital gains

GOOGL-1998
No capital gains

"""
