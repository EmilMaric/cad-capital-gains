from click import ClickException
from datetime import date
import pytest
from capgains.transaction import Transaction
from capgains.transactions_reader import TransactionsReader
from tests.helpers import create_csv_file, transactions_to_list


def test_transactions_reader_default(testfiles_dir, transactions):
    """Testing TransactionsReader for a valid csv file"""
    exp_transaction = Transaction(date(2018, 2, 15),
                                  'ESPP PURCHASE',
                                  'ANET',
                                  'BUY',
                                  21,
                                  307.96,
                                  20.99)
    transactions_list = transactions_to_list([exp_transaction])
    filepath = create_csv_file(testfiles_dir,
                               "good.csv",
                               transactions_list,
                               True)

    actual_transactions = TransactionsReader.get_transactions(filepath)
    assert len(actual_transactions) == 1
    actual_transaction = actual_transactions[0]
    assert actual_transaction.to_dict() == exp_transaction.to_dict()


def test_transactions_reader_columns_error(testfiles_dir):
    """Testing TransactionsReader for a csv file with too many columns"""
    transaction = Transaction(date(2018, 2, 15),
                              'ESPP PURCHASE',
                              'ANET',
                              'BUY',
                              21,
                              307.96,
                              20.99)
    transactions_list = transactions_to_list([transaction])
    # Add an extra column to the transaction
    transactions_list[0].append('EXTRA_COLUMN_VALUE')
    with pytest.raises(ClickException):
        filepath = create_csv_file(testfiles_dir,
                                   "too_many_cols.csv",
                                   transactions_list,
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


def test_transactions_read_wrong_dates_order(testfiles_dir):
    """Testing TransactionsReader with out of order dates"""
    transaction_after = Transaction(date(2018, 2, 20),
                                    'RSU VEST',
                                    'GOOGL',
                                    'BUY',
                                    42,
                                    249.55,
                                    0.0)
    transaction_before = Transaction(date(2018, 2, 15),
                                     'ESPP PURCHASE',
                                     'ANET',
                                     'BUY',
                                     21,
                                     307.96,
                                     20.99)
    transactions_list = transactions_to_list([transaction_after,
                                             transaction_before])
    with pytest.raises(ClickException):
        filepath = create_csv_file(testfiles_dir,
                                   "outoforder.csv,",
                                   transactions_list,
                                   True)
        TransactionsReader.get_transactions(filepath)
