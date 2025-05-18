from click import ClickException
from datetime import date
import pytest
import json
from decimal import Decimal

from capgains.transaction import Transaction
from capgains.transactions_reader import TransactionsReader
from tests.helpers import create_csv_file, create_json_file, transactions_to_list


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_default(testfiles_dir, transactions, create_file):
    """Testing TransactionsReader for valid input files"""
    exp_transaction = Transaction(date(2018, 2, 15),
                                  'ESPP PURCHASE',
                                  'ANET',
                                  'BUY',
                                  21,
                                  307.96,
                                  20.99,
                                  'USD')
    exp_transactions = transactions_to_list([exp_transaction])
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"good{ext}",
                           exp_transactions,
                           True)

    actual_transactions = TransactionsReader.get_transactions(filepath)
    assert len(actual_transactions) == 1
    actual_transaction = actual_transactions[0]
    assert actual_transaction.__dict__ == exp_transaction.__dict__


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_columns_error(testfiles_dir, create_file):
    """Testing TransactionsReader for input files with too many columns"""
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
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"too_many_cols{ext}",
                           transactions,
                           True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "Transaction entry 0: expected 8 columns, entry has 9"


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_file_not_found_error(testfiles_dir, create_file):
    """Testing TransactionsReader with a non-existent file"""
    ext = '.json' if create_file == create_json_file else '.csv'
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(create_file(testfiles_dir,
                                                        f"dne{ext}"))
    assert excinfo.value.message == "File not found: {}/{}".format(
        testfiles_dir, f"dne{ext}")


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_OS_error(testfiles_dir, create_file):
    """Testing TransactionsReader for an unreadable file"""
    ext = '.json' if create_file == create_json_file else '.csv'
    with pytest.raises(OSError):
        TransactionsReader.get_transactions(create_file(testfiles_dir,
                                                        f"unreadable{ext}",
                                                        is_readable=False))


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_read_wrong_dates_order(testfiles_dir, create_file):
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
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"outoforder{ext}",
                           transactions,
                           True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "Transactions were not entered in chronological order"


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_date_wrong_format(testfiles_dir, create_file):
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
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"datewrongformat{ext}",
                           transactions,
                           True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The date (January 1st 2020) was not entered in the correct format (YYYY-MM-DD)"


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_qty_not_number(testfiles_dir, create_file):
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
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"qtynotinteger{ext}",
                           transactions,
                           True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The quantity entered BLAH is not a valid number"


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_price_not_number(testfiles_dir, create_file):
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
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"pricenotfloat{ext}",
                           transactions,
                           True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The price entered BLAH is not a valid number"


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_commission_not_number(testfiles_dir, create_file):
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
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir,
                           f"commissionnotfloat{ext}",
                           transactions,
                           True)
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The commission entered BLAH is not a valid number"


def test_transactions_reader_json(testfiles_dir):
    """Testing TransactionsReader for a valid JSON file"""
    exp_transaction = Transaction(
        date(2018, 2, 15),
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        21,
        Decimal('307.96'),
        Decimal('20.99'),
        'USD'
    )

    # Create test JSON file
    json_data = [{
        "date": "2018-02-15",
        "description": "ESPP PURCHASE",
        "ticker": "ANET",
        "action": "BUY",
        "qty": "21",
        "price": "307.96",
        "commission": "20.99",
        "currency": "USD"
    }]

    filepath = str(testfiles_dir.join('test.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    actual_transactions = TransactionsReader.get_transactions(filepath)
    assert len(actual_transactions) == 1
    actual_transaction = actual_transactions[0]
    
    # Compare fields individually to avoid decimal precision issues
    assert actual_transaction.date == exp_transaction.date
    assert actual_transaction.description == exp_transaction.description
    assert actual_transaction.ticker == exp_transaction.ticker
    assert actual_transaction.action == exp_transaction.action
    assert actual_transaction.qty == exp_transaction.qty
    assert actual_transaction.price == exp_transaction.price
    assert actual_transaction.commission == exp_transaction.commission
    assert actual_transaction.currency == exp_transaction.currency


def test_transactions_reader_json_missing_fields(testfiles_dir):
    """Testing TransactionsReader for a JSON file with missing fields"""
    # Create test JSON file with missing fields
    json_data = [{
        "date": "2018-02-15",
        "description": "ESPP PURCHASE",
        "ticker": "ANET",
        # Missing action field
        "qty": 21,
        "price": 307.96,
        "commission": 20.99,
        "currency": "USD"
    }]

    filepath = str(testfiles_dir.join('invalid.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert "missing required fields: action" in excinfo.value.message


def test_transactions_reader_json_invalid_date(testfiles_dir):
    """Testing TransactionsReader for a JSON file with invalid date format"""
    json_data = [{
        "date": "15-02-2018",  # Wrong date format
        "description": "ESPP PURCHASE",
        "ticker": "ANET",
        "action": "BUY",
        "qty": 21,
        "price": 307.96,
        "commission": 20.99,
        "currency": "USD"
    }]

    filepath = str(testfiles_dir.join('invalid_date.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert "not entered in the correct format" in excinfo.value.message


def test_transactions_reader_json_invalid_numeric(testfiles_dir):
    """Testing TransactionsReader for a JSON file with invalid numeric values"""
    json_data = [{
        "date": "2018-02-15",
        "description": "ESPP PURCHASE",
        "ticker": "ANET",
        "action": "BUY",
        "qty": "invalid",  # Invalid quantity
        "price": 307.96,
        "commission": 20.99,
        "currency": "USD"
    }]

    filepath = str(testfiles_dir.join('invalid_numeric.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert excinfo.value.message == "The quantity entered invalid is not a valid number"


def test_transactions_reader_json_not_chronological(testfiles_dir):
    """Testing TransactionsReader for a JSON file with out-of-order dates"""
    json_data = [
        {
            "date": "2018-02-15",
            "description": "First Transaction",
            "ticker": "ANET",
            "action": "BUY",
            "qty": 21,
            "price": 307.96,
            "commission": 20.99,
            "currency": "USD"
        },
        {
            "date": "2018-02-14",  # Earlier date than previous transaction
            "description": "Second Transaction",
            "ticker": "ANET",
            "action": "BUY",
            "qty": 21,
            "price": 307.96,
            "commission": 20.99,
            "currency": "USD"
        }
    ]

    filepath = str(testfiles_dir.join('not_chronological.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert "not entered in chronological order" in excinfo.value.message
