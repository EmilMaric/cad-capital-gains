import pytest
from datetime import date

from capgains.transaction import Transaction


@pytest.fixture(scope="session")
def testfiles_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("testfiles")


@pytest.fixture(scope='module')
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
    ]
    return trans


@pytest.fixture(scope='module')
def acb_transactions():
    trans = [
        Transaction(
            date(2018, 2, 15),
            'ESPP PURCHASE',
            'ANET',
            'BUY',
            21,
            307.96,
            0.00,
        ),
        Transaction(
            date(2018, 2, 20),
            'RSU VEST',
            'ANET',
            'BUY',
            42,
            249.65,
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
            date(2018, 2, 20),
            'RSU VEST',
            'GOOGL',
            'BUY',
            42,
            249.55,
            0.00,
        ),
    ]
    return trans
