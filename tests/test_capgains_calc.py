import capgains.commands.capgains_calc as CapGainsCalc
import requests_mock as rm


def mock_exchange_rates(transactions, mocker):
    observations = []
    for transaction in transactions:
        observations.append(
            {
                "d": transaction.date.isoformat(),
                "FXUSDCAD": {
                    "v": "1.1"
                }
            })
    mocker.get(rm.ANY, json={"observations": observations})


def test_ticker(transactions, capfd, requests_mock):
    """Testing capgains_calc without any optional filters"""
    mock_exchange_rates(transactions, requests_mock)
    CapGainsCalc.capgains_calc(transactions, 2018, ['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
date        transaction_type    ticker    action      qty    price    commission    share_balance    proceeds    capital_gain    acb_delta     acb
----------  ------------------  --------  --------  -----  -------  ------------  ---------------  ----------  --------------  -----------  ------
2018-02-20  RSU VEST            ANET      SELL         20   249.00         20.31                1    5,455.66       -1,297.47    -6,753.13  337.66

"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_show without any transactions"""
    CapGainsCalc.capgains_calc([], 2018)
    out, _ = capfd.readouterr()
    assert out == """\
No calculations made
"""


def test_unknown_year(transactions, capfd, requests_mock):
    """Testing capgains_show with a year matching no transactions"""
    mock_exchange_rates(transactions, requests_mock)
    CapGainsCalc.capgains_calc(transactions, 1998)
    out, _ = capfd.readouterr()
    assert out == """\
No calculations made
"""
