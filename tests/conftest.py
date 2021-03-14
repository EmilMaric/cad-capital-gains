import pytest
import requests_mock as rm
from datetime import date

from capgains.transaction import Transaction
from capgains.transactions import Transactions


@pytest.fixture(scope="session")
def testfiles_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("testfiles")


@pytest.fixture(scope='function')
def transactions():
    trans = [
        Transaction(
            date(2017, 2, 15),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            100,
            50.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 2, 20),
            'RSU VEST',
            'GOOGL',
            'BUY',
            30,
            20.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2018, 2, 20),
            'RSU VEST',
            'ANET',
            'SELL',
            50,
            120.00,
            10.00,
            'USD'
        ),
        Transaction(
            date(2019, 2, 15),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            50,
            130.00,
            10.00,
            'USD'
        )
    ]
    return Transactions(trans)


@pytest.fixture(scope='function')
def exchange_rates_mock(requests_mock, transactions):
    observations = []
    for transaction in transactions:
        observations.append({
            'd': transaction.date.isoformat(),
            'FXUSDCAD': {
                'v': '2.0'
            }
        })
    requests_mock.get(rm.ANY, json={"observations": observations})
