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
                                  20.99,
                                  'USD')
    exp_transactions = transactions_to_list([exp_transaction])
    filepath = create_csv_file(testfiles_dir,
                               "good.csv",
                               exp_transactions,
                               True)

    actual_transactions = TransactionsReader.get_transactions(filepath)
    assert len(actual_transactions) == 1
    actual_transaction = actual_transactions[0]
    assert actual_transaction.__dict__ == exp_transaction.__dict__


def test_transactions_reader_columns_error(testfiles_dir):
    """Testing TransactionsReader for a csv file with too many columns"""
    transaction = Transaction(date(2018, 2, 15),
                              'ESPP PURCHASE',
                              'ANET',
                              'BUY',
                              21,
                              307.96,
                              20.99,
                              'USD')
    transactions = transactions_to_list([transaction])
    # Add an extra column to the transaction
    transactions[0].append('EXTRA_COLUMN_VALUE')
    filepath = create_csv_file(testfiles_dir,
                               "too_many_cols.csv",
                               transactions,
                               True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "Transaction entry 0: expected 8 columns, entry has 9"  # noqa: E501


def test_transactions_reader_file_not_found_error(testfiles_dir):
    """Testing TransactionsReader with a non-existent file"""
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(create_csv_file(testfiles_dir,
                                                            "dne.csv"))
    assert excinfo.value.message == "File not found: {}/{}".format(
        testfiles_dir, "dne.csv")


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
                                    0.0,
                                    'USD')
    transaction_before = Transaction(date(2018, 2, 15),
                                     'ESPP PURCHASE',
                                     'ANET',
                                     'BUY',
                                     21,
                                     307.96,
                                     20.99,
                                     'USD')
    transactions = transactions_to_list([transaction_after,
                                         transaction_before])
    filepath = create_csv_file(testfiles_dir,
                               "outoforder.csv,",
                               transactions,
                               True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "Transactions were not entered in chronological order"  # noqa: E501


def test_transactions_date_wrong_format(testfiles_dir):
    """Testing TransactionsReader with dates entered in wrong format"""
    transaction = Transaction('January 1st 2020',
                              'RSU VEST',
                              'ANET',
                              'BUY',
                              100,
                              50.00,
                              0.0,
                              'USD')
    transactions = transactions_to_list([transaction])
    filepath = create_csv_file(testfiles_dir,
                               "datewrongformat.csv,",
                               transactions,
                               True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The date (January 1st 2020) was not entered in the correct format (YYYY-MM-DD)"  # noqa: E501


def test_transactions_qty_not_number(testfiles_dir):
    """Testing TransactionsReader with qty entered in wrong format"""
    transaction = Transaction(date(2020, 2, 20),
                              'RSU VEST',
                              'ANET',
                              'BUY',
                              100.1,
                              50.00,
                              0.0,
                              'USD')
    # Overwrite the qty after creating the object because otherwise the object
    # initialization will throw an error
    transaction._qty = 'BLAH'
    transactions = transactions_to_list([transaction])
    filepath = create_csv_file(testfiles_dir,
                               "qtynotinteger.csv,",
                               transactions,
                               True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The quantity entered BLAH is not a valid number"  # noqa: E501


def test_transactions_price_not_number(testfiles_dir):
    """Testing TransactionsReader with price entered in wrong format"""
    transaction = Transaction(date(2020, 2, 20),
                              'RSU VEST',
                              'ANET',
                              'BUY',
                              100,
                              100,
                              0.0,
                              'USD')
    # Overwrite the price after creating the object because otherwise the
    # object initialization will throw an error
    transaction._price = 'BLAH'
    transactions = transactions_to_list([transaction])
    filepath = create_csv_file(testfiles_dir,
                               "pricenotfloat.csv,",
                               transactions,
                               True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The price entered BLAH is not a valid number"  # noqa: E501


def test_transactions_commission_not_number(testfiles_dir):
    """Testing TransactionsReader with commission entered in wrong format"""
    transaction = Transaction(date(2020, 2, 20),
                              'RSU VEST',
                              'ANET',
                              'BUY',
                              100,
                              50.00,
                              0.0,
                              'USD')
    # Overwrite the commission after creating the object because otherwise the
    # object initialization will throw an error
    transaction._commission = 'BLAH'
    transactions = transactions_to_list([transaction])
    filepath = create_csv_file(testfiles_dir,
                               "commissionnotfloat.csv,",
                               transactions,
                               True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The commission entered BLAH is not a valid number"  # noqa: E501
