from click import ClickException
from datetime import datetime as dt
import pytest
from capgains.transactions_reader import TransactionsReader
from tests.helpers import create_csv_file


def test_transactions_reader_default(testfiles_dir):
    """Testing TransactionsReader for a valid csv file"""
    filepath = create_csv_file(testfiles_dir,
                               "good.csv",
                               [[dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
                                 'ESPP PURCHASE',
                                 'ANET',
                                 'BUY',
                                 '21',
                                 '307.96',
                                 '20.99']],
                               True)

    assert len(TransactionsReader.get_transactions(filepath)) == 1


def test_transactions_reader_columns_error(testfiles_dir):
    """Testing TransactionsReader for a csv file with too many columns"""
    with pytest.raises(ClickException):
        filepath = create_csv_file(testfiles_dir,
                                   "too_many_cols.csv",
                                   [[dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
                                     'ESPP PURCHASE',
                                     'ANET',
                                     'BUY',
                                     '21',
                                     '307.96',
                                     '20.99',
                                     'EXTRA_COLUMN_VALUE']],
                                   True)
        TransactionsReader.get_transactions(filepath)


def test_transactions_reader_file_not_found_error(testfiles_dir):
    """Testing TransactionsReader with a non-existent file"""
    with pytest.raises(ClickException):
        TransactionsReader.get_transactions(create_csv_file(testfiles_dir,
                                                            "dne.csv"))


def test_transactions_reader_OS_error(testfiles_dir):
    """Testing TransactionsReader for an unreadable file"""
    with pytest.raises(OSError):
        TransactionsReader.get_transactions(create_csv_file(testfiles_dir,
                                                            "unreadable.csv",
                                                            is_readable=False))
