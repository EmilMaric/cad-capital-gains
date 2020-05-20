from click import ClickException
import os
import csv
from datetime import datetime as dt
import pytest
from capgains.transactions_reader import TransactionsReader


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


def test_transactions_reader_default(good_csv_file_path):
    assert len(TransactionsReader.get_transactions(good_csv_file_path)) == 1


def test_transactions_reader_columns_error(too_many_columns_csv_file_path):
    with pytest.raises(ClickException):
        TransactionsReader.get_transactions(too_many_columns_csv_file_path)


def test_transactions_reader_file_not_found_error(non_existent_file_path):
    with pytest.raises(ClickException):
        TransactionsReader.get_transactions(non_existent_file_path)


def test_transactions_reader_OS_error(unreadable_file_path):
    with pytest.raises(OSError):
        TransactionsReader.get_transactions(unreadable_file_path)
