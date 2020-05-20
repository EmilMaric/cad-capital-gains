import pytest
from datetime import datetime as dt

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
