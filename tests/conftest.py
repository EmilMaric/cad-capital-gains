import pytest
from datetime import date

from capgains.transaction import Transaction


@pytest.fixture(scope="session")
def testfiles_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("testfiles")


@pytest.fixture(scope='function')
def transactions():
    trans = [
        Transaction(
            date(2018, 2, 15),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            21,
            307.96,
            20.99,
        ),
        Transaction(
            date(2018, 2, 20),
            'RSU VEST',
            'GOOGL',
            'BUY',
            42,
            249.55,
            0.00,
        ),
        Transaction(
            date(2018, 2, 20),
            'RSU VEST',
            'ANET',
            'SELL',
            20,
            249.00,
            20.31,
        ),
        Transaction(
            date(2019, 2, 15),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            21,
            307.96,
            20.99,
        )
    ]
    return trans


@pytest.fixture(scope='function')
def transactions_as_list(transactions):
    as_list = []
    for transaction in transactions:
        as_list.append(transaction.to_list())
    return as_list
