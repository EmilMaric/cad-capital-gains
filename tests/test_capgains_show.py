import capgains.commands.capgains_show as CapGainsShow
from datetime import datetime as dt
import pytest
from click import ClickException
import os
import csv

from capgains.transaction import Transaction
from capgains.transactions_reader import TransactionsReader


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


@pytest.fixture(scope='session')
def good_csv_file_path(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("testfiles").join("too_many_cols.csv"))

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
                         'ESPP PURCHASE',
                         'ANET',
                         'BUY',
                         '21',
                         '307.96',
                         '20.99'])
    return path


@pytest.fixture(scope='session')
def too_many_columns_csv_file_path(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("testfiles").join("too_many_cols.csv"))

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
                         'ESPP PURCHASE',
                         'ANET',
                         'BUY',
                         '21',
                         '307.96',
                         '20.99',
                         'EXTRA_COLUMN_VALUE'])
    return path


@pytest.fixture(scope='session')
def non_existent_file_path(tmpdir_factory):
    return str(tmpdir_factory.mktemp("testfiles").join("dne.csv"))


@pytest.fixture(scope='session')
def unreadable_file_path(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("testfiles").join("unreadable.csv"))

    # actually create the file
    open(path, 'a').close()

    # set permissions to chmod 000
    os.chmod(path, 000)

    return path


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


def test_transactions_to_dict(transactions):
    trans_dict = transactions[0].to_dict()

    assert trans_dict['date'] == '2018-02-15'
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == '21'
    assert trans_dict['price'] == '307.96'
    assert trans_dict['commission'] == '20.99'

    # check that no extra values we added
    assert len(trans_dict) == Transaction.num_vals


def test_transactions_reader_default(good_csv_file_path):
    transactions = TransactionsReader.get_transactions(good_csv_file_path)

    assert len(transactions) == 1


def test_transactions_reader_columns_error(too_many_columns_csv_file_path):
    with pytest.raises(ClickException):
        TransactionsReader.get_transactions(too_many_columns_csv_file_path)


def test_transactions_reader_file_not_found_error(non_existent_file_path):
    with pytest.raises(ClickException):
        TransactionsReader.get_transactions(non_existent_file_path)


def test_transactions_reader_OS_error(unreadable_file_path):
    with pytest.raises(OSError):
        TransactionsReader.get_transactions(unreadable_file_path)
