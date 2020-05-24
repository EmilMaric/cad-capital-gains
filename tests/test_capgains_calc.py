import pytest
import capgains.commands.capgains_calc as CapGainsCalc
from capgains.transaction import Transaction
from datetime import date


def test_ticker(acb_transactions, capfd):
    """Testing capgains_calc without any optional filters"""
    CapGainsCalc.capgains_calc(acb_transactions, 2018, ['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
date        transaction_type    ticker    action      qty    price    commission    share_balance    proceeds    capital_gain    acb_delta        acb
----------  ------------------  --------  --------  -----  -------  ------------  ---------------  ----------  --------------  -----------  ---------
2018-02-20  RSU VEST            ANET      SELL         20   249.00         20.31               43    6,260.12         -509.09    -6,769.21  14,553.81

"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_show without any transactions"""
    CapGainsCalc.capgains_calc([], 2018)
    out, _ = capfd.readouterr()
    assert out == """\
No calculations made
"""


def test_unknown_year(acb_transactions, capfd):
    """Testing capgains_show with a year matching no transactions"""
    CapGainsCalc.capgains_calc(acb_transactions, 1998)
    out, _ = capfd.readouterr()
    assert out == """\
No calculations made
"""