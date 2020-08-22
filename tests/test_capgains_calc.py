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


def test_ticker(acb_transactions, capfd, requests_mock):
    """Testing capgains_calc without any optional filters"""
    mock_exchange_rates(acb_transactions, requests_mock)
    CapGainsCalc.capgains_calc(acb_transactions, 2018, ['ANET'])
    out, _ = capfd.readouterr()
    assert out == """\
ANET-2018
date        transaction_type    ticker    action      qty    price    commission    share_balance    proceeds    capital_gain    acb_delta        acb
----------  ------------------  --------  --------  -----  -------  ------------  ---------------  ----------  --------------  -----------  ---------
2018-02-20  RSU VEST            ANET      SELL         20   249.00         20.31               43    5,455.66         -464.25    -5,919.91  12,727.80

"""  # noqa: E501


def test_no_transactions(capfd):
    """Testing capgains_show without any transactions"""
    CapGainsCalc.capgains_calc([], 2018)
    out, _ = capfd.readouterr()
    assert out == """\
No calculations made
"""


def test_unknown_year(acb_transactions, capfd, requests_mock):
    """Testing capgains_show with a year matching no transactions"""
    mock_exchange_rates(acb_transactions, requests_mock)
    CapGainsCalc.capgains_calc(acb_transactions, 1998)
    out, _ = capfd.readouterr()
    assert out == """\
No calculations made
"""
