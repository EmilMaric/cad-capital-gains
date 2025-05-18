from click import ClickException
from datetime import date
import pytest
import json
from decimal import Decimal

from capgains.transaction import Transaction
from capgains.transactions_reader import TransactionsReader
from tests.helpers import (
    create_csv_file, create_json_file, transactions_to_list
)


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_default(testfiles_dir, transactions, create_file):
    """Testing TransactionsReader for valid input files.

    This test verifies that the TransactionsReader can correctly read and
    parse a valid input file.
    """
    exp_transaction = Transaction(
        date(2018, 2, 15),
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        21,
        307.96,
        20.99,
        'USD'
    )
    exp_transactions = transactions_to_list([exp_transaction])
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(testfiles_dir, f"good{ext}", exp_transactions, True)

    actual_transactions = TransactionsReader.get_transactions(filepath)
    assert len(actual_transactions) == 1
    actual_transaction = actual_transactions[0]
    assert actual_transaction.__dict__ == exp_transaction.__dict__


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_columns_error(testfiles_dir, create_file):
    """Testing TransactionsReader for input files with too many columns.

    This test verifies that the appropriate error is raised when a transaction
    entry has more columns than expected.
    """
    transaction = Transaction(
        date(2018, 2, 15),
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        21,
        307.96,
        20.99,
        'USD'
    )
    transactions = transactions_to_list([transaction])
    # Add an extra column to the transaction
    transactions[0].append('EXTRA_COLUMN_VALUE')
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(
        testfiles_dir, f"too_many_cols{ext}", transactions, True
    )
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = ("Transaction entry 0: expected 8 columns, entry has 9")
    assert excinfo.value.message == error_msg


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_file_not_found_error(testfiles_dir, create_file):
    """Testing TransactionsReader with a non-existent file.

    This test verifies that the appropriate error is raised when attempting
    to read a file that does not exist.
    """
    ext = '.json' if create_file == create_json_file else '.csv'
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(
            create_file(testfiles_dir, f"dne{ext}")
        )
    error_msg = "File not found: {}/{}".format(testfiles_dir, f"dne{ext}")
    assert excinfo.value.message == error_msg


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_reader_OS_error(testfiles_dir, create_file):
    """Testing TransactionsReader for an unreadable file.

    This test verifies that the appropriate error is raised when attempting
    to read a file that cannot be read.
    """
    ext = '.json' if create_file == create_json_file else '.csv'
    with pytest.raises(OSError):
        TransactionsReader.get_transactions(
            create_file(testfiles_dir, f"unreadable{ext}", is_readable=False)
        )


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_read_wrong_dates_order(testfiles_dir, create_file):
    """Testing TransactionsReader with out of order dates.

    This test verifies that transactions must be entered in chronological
    order.
    """
    transaction_after = Transaction(
        date(2018, 2, 20), 'RSU VEST', 'GOOGL', 'BUY', 42, 249.55, 0.0, 'USD'
    )
    transaction_before = Transaction(
        date(2018, 2, 15),
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        21,
        307.96,
        20.99,
        'USD'
    )
    transactions = transactions_to_list(
        [transaction_after, transaction_before]
    )
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(
        testfiles_dir, f"outoforder{ext}", transactions, True
    )
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = ("Transactions are not in chronological order")
    assert excinfo.value.message == error_msg


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_date_wrong_format(testfiles_dir, create_file):
    """Testing TransactionsReader with dates entered in wrong format.

    This test verifies that dates must be entered in YYYY-MM-DD format.
    """
    transaction = Transaction(
        'January 1st 2020', 'RSU VEST', 'ANET', 'BUY', 100, 50.00, 0.0, 'USD'
    )
    transactions = transactions_to_list([transaction])
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(
        testfiles_dir, f"datewrongformat{ext}", transactions, True
    )
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = (
        "The date (January 1st 2020) was not entered in the "
        "correct format (YYYY-MM-DD)"
    )
    assert excinfo.value.message == error_msg


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_qty_not_number(testfiles_dir, create_file):
    """Testing TransactionsReader with qty entered in wrong format.

    This test verifies that quantity must be a valid number.
    """
    transaction = Transaction(
        date(2020, 2, 20), 'RSU VEST', 'ANET', 'BUY', 100.1, 50.00, 0.0, 'USD'
    )
    # Overwrite the qty after creating the object because otherwise the object
    # initialization will throw an error
    transaction._qty = 'BLAH'
    transactions = transactions_to_list([transaction])
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(
        testfiles_dir, f"qtynotinteger{ext}", transactions, True
    )
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = ("The quantity entered BLAH is not a valid number")
    assert excinfo.value.message == error_msg


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_price_not_number(testfiles_dir, create_file):
    """Testing TransactionsReader with price entered in wrong format.

    This test verifies that price must be a valid number.
    """
    transaction = Transaction(
        date(2020, 2, 20), 'RSU VEST', 'ANET', 'BUY', 100, 100, 0.0, 'USD'
    )
    # Overwrite the price after creating the object because otherwise the
    # object initialization will throw an error
    transaction._price = 'BLAH'
    transactions = transactions_to_list([transaction])
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(
        testfiles_dir, f"pricenotfloat{ext}", transactions, True
    )
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = ("The price entered BLAH is not a valid number")
    assert excinfo.value.message == error_msg


@pytest.mark.parametrize("create_file", [create_csv_file, create_json_file])
def test_transactions_commission_not_number(testfiles_dir, create_file):
    """Testing TransactionsReader with commission entered in wrong format.

    This test verifies that commission must be a valid number.
    """
    transaction = Transaction(
        date(2020, 2, 20), 'RSU VEST', 'ANET', 'BUY', 100, 50.00, 0.0, 'USD'
    )
    # Overwrite the commission after creating the object because otherwise the
    # object initialization will throw an error
    transaction._commission = 'BLAH'
    transactions = transactions_to_list([transaction])
    ext = '.json' if create_file == create_json_file else '.csv'
    filepath = create_file(
        testfiles_dir, f"commissionnotfloat{ext}", transactions, True
    )
    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = ("The commission entered BLAH is not a valid number")
    assert excinfo.value.message == error_msg


def test_transactions_reader_json(testfiles_dir):
    """Testing TransactionsReader for a valid JSON file.

    This test verifies that the TransactionsReader can correctly read and
    parse a valid JSON file.
    """
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
    json_data = [
        {
            "date": "2018-02-15",
            "description": "ESPP PURCHASE",
            "ticker": "ANET",
            "action": "BUY",
            "qty": "21",
            "price": "307.96",
            "commission": "20.99",
            "currency": "USD"
        }
    ]

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
    """Testing TransactionsReader for a JSON file with missing fields.

    This test verifies that the appropriate error is raised when a JSON file
    is missing required fields.
    """
    # Create test JSON file with missing fields
    json_data = [
        {
            "date": "2018-02-15",
            "description": "ESPP PURCHASE",
            "ticker": "ANET",  # Missing action field
            "qty": 21,
            "price": 307.96,
            "commission": 20.99,
            "currency": "USD"
        }
    ]

    filepath = str(testfiles_dir.join('invalid.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert "missing required fields: action" in excinfo.value.message


def test_transactions_reader_json_invalid_date(testfiles_dir):
    """Testing TransactionsReader for a JSON file with invalid date format.

    This test verifies that the appropriate error is raised when a JSON file
    contains dates in an invalid format.
    """
    json_data = [
        {
            "date": "15-02-2018",  # Wrong date format
            "description": "ESPP PURCHASE",
            "ticker": "ANET",
            "action": "BUY",
            "qty": 21,
            "price": 307.96,
            "commission": 20.99,
            "currency": "USD"
        }
    ]

    filepath = str(testfiles_dir.join('invalid_date.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert "not entered in the correct format" in excinfo.value.message


def test_transactions_reader_json_invalid_numeric(testfiles_dir):
    """Testing TransactionsReader for a JSON file with invalid numeric
    values.

    This test verifies that the appropriate error is raised when a JSON file
    contains invalid numeric values.
    """
    json_data = [
        {
            "date": "2018-02-15",
            "description": "ESPP PURCHASE",
            "ticker": "ANET",
            "action": "BUY",
            "qty": "invalid",  # Invalid quantity
            "price": 307.96,
            "commission": 20.99,
            "currency": "USD"
        }
    ]

    filepath = str(testfiles_dir.join('invalid_numeric.json'))
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    error_msg = ("The quantity entered invalid is not a valid number")
    assert excinfo.value.message == error_msg


def test_transactions_reader_json_not_chronological(testfiles_dir):
    """Testing TransactionsReader for a JSON file with out-of-order dates.

    This test verifies that transactions in a JSON file must be in
    chronological order.
    """
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
    error_msg = ("Transactions are not in chronological order")
    assert excinfo.value.message == error_msg


def test_transactions_reader_csv_with_header(testfiles_dir):
    """Testing TransactionsReader rejects CSV files with headers.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    # Create a CSV file with a header row
    header_row = [
        'date',
        'description',
        'ticker',
        'action',
        'qty',
        'price',
        'commission',
        'currency'
    ]
    transaction_row = [
        '2018-02-15',
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        '21',
        '307.96',
        '20.99',
        'USD'
    ]

    filepath = create_csv_file(
        testfiles_dir, 'with_header.csv', [header_row, transaction_row], True
    )

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message


def test_transactions_reader_csv_with_text_headers(testfiles_dir):
    """Testing TransactionsReader rejects CSV files with text headers like
    'Date,Description,...'.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    # Create a CSV file with text headers
    header_row = [
        'Date',
        'Description',
        'Ticker',
        'Action',
        'Quantity',
        'Price',
        'Commission',
        'Currency'
    ]
    transaction_row = [
        '2018-02-15',
        'ESPP PURCHASE',
        'ANET',
        'BUY',
        '21',
        '307.96',
        '20.99',
        'USD'
    ]

    filepath = create_csv_file(
        testfiles_dir,
        'with_text_header.csv', [header_row, transaction_row],
        True
    )

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(filepath)
    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message


def test_invalid_json_format(tmp_path):
    """Test handling of invalid JSON format.

    This test verifies that the appropriate error is raised when a JSON file
    contains invalid JSON format.
    """
    json_path = tmp_path / "invalid.json"
    with open(json_path, "w") as f:
        f.write("invalid json")

    with pytest.raises(ClickException,
                       match=f"Invalid JSON format in file: {json_path}"):
        TransactionsReader.get_transactions(json_path)


def test_json_not_list(tmp_path):
    """Test handling of JSON that is not a list.

    This test verifies that the appropriate error is raised when a JSON file
    does not contain a list of transactions.
    """
    json_path = tmp_path / "not_list.json"
    with open(json_path, "w") as f:
        json.dump({"not": "a list"}, f)

    with pytest.raises(ClickException,
                       match="JSON file must contain a list of txs"):
        TransactionsReader.get_transactions(json_path)


def test_json_missing_fields(tmp_path):
    """Test handling of JSON entries with missing required fields.

    This test verifies that the appropriate error is raised when a JSON entry
    is missing required fields.
    """
    json_path = tmp_path / "missing_fields.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "2022-01-01",
                    "description": "Buy AAPL",  # Missing ticker field
                    "action": "BUY",
                    "qty": 100,
                    "price": 150.00,
                    "commission": 9.99,
                    "currency": "USD"
                }
            ],
            f
        )

    with pytest.raises(
            ClickException,
            match=("Transaction entry 0: missing required fields: ticker")):
        TransactionsReader.get_transactions(json_path)


def test_json_extra_fields(tmp_path):
    """Test handling of JSON entries with extra fields.

    This test verifies that the appropriate error is raised when a JSON entry
    has more columns than expected.
    """
    json_path = tmp_path / "extra_fields.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "2022-01-01",
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": 100,
                    "price": 150.00,
                    "commission": 9.99,
                    "currency": "USD",
                    "extra": "field"  # Extra field
                }
            ],
            f
        )

    with pytest.raises(
            ClickException,
            match=("Transaction entry 0: expected 8 columns, entry has 9")):
        TransactionsReader.get_transactions(json_path)


def test_json_invalid_date(tmp_path):
    """Test handling of JSON entries with invalid date format.

    This test verifies that the appropriate error is raised when a JSON entry
    contains dates in an invalid format.
    """
    json_path = tmp_path / "invalid_date.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "01/01/2022",  # Wrong format
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": 100,
                    "price": 150.00,
                    "commission": 9.99,
                    "currency": "USD"
                }
            ],
            f
        )

    with pytest.raises(
            ClickException,
            match=("The date \\(01/01/2022\\) was not entered in the correct "
                   "format \\(YYYY-MM-DD\\)")):
        TransactionsReader.get_transactions(json_path)


def test_json_invalid_quantity(tmp_path):
    """Test handling of JSON entries with invalid quantity.

    This test verifies that the appropriate error is raised when a JSON entry
    contains an invalid quantity format.
    """
    json_path = tmp_path / "invalid_qty.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "2022-01-01",
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": "not a number",
                    "price": 150.00,
                    "commission": 9.99,
                    "currency": "USD"
                }
            ],
            f
        )

    with pytest.raises(
            ClickException,
            match=("The quantity entered not a number is not a valid number")):
        TransactionsReader.get_transactions(json_path)


def test_json_invalid_price(tmp_path):
    """Test handling of JSON entries with invalid price.

    This test verifies that the appropriate error is raised when a JSON entry
    contains an invalid price format.
    """
    json_path = tmp_path / "invalid_price.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "2022-01-01",
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": 100,
                    "price": "not a number",
                    "commission": 9.99,
                    "currency": "USD"
                }
            ],
            f
        )

    with pytest.raises(
            ClickException,
            match=("The price entered not a number is not a valid number")):
        TransactionsReader.get_transactions(json_path)


def test_json_invalid_commission(tmp_path):
    """Test handling of JSON entries with invalid commission.

    This test verifies that the appropriate error is raised when a JSON entry
    contains an invalid commission format.
    """
    json_path = tmp_path / "invalid_commission.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "2022-01-01",
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": 100,
                    "price": 150.00,
                    "commission": "not a number",
                    "currency": "USD"
                }
            ],
            f
        )

    with pytest.raises(
            ClickException,
            match=(
                "The commission entered not a number is not a valid number")):
        TransactionsReader.get_transactions(json_path)


def test_json_chronological_order(tmp_path):
    """Test handling of JSON entries not in chronological order.

    This test verifies that the appropriate error is raised when transactions
    in a JSON file are not in chronological order.
    """
    json_path = tmp_path / "not_chronological.json"
    with open(json_path, "w") as f:
        json.dump(
            [
                {
                    "date": "2022-02-01",
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": 100,
                    "price": 150.00,
                    "commission": 9.99,
                    "currency": "USD"
                },
                {
                    "date": "2022-01-01",  # Earlier date
                    "description": "Buy AAPL",
                    "ticker": "AAPL",
                    "action": "BUY",
                    "qty": 100,
                    "price": 150.00,
                    "commission": 9.99,
                    "currency": "USD"
                }
            ],
            f
        )

    with pytest.raises(ClickException,
                       match="Transactions are not in chronological order"):
        TransactionsReader.get_transactions(json_path)


def test_csv_header_detection_with_date_field(tmp_path):
    """Test detection of header row when first row contains 'date' field.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    csv_path = tmp_path / "header.csv"
    with open(csv_path, "w") as f:
        f.write(
            "date,description,ticker,action,quantity,price,commission,"
            "currency\n"
            "2022-01-01,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD"
        )

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(csv_path)

    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message


def test_csv_header_detection_with_qty_field(tmp_path):
    """Test detection of header row when first row contains 'qty' field.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    csv_path = tmp_path / "header.csv"
    with open(csv_path, "w") as f:
        f.write(
            "date,description,ticker,action,qty,price,commission,"
            "currency\n"
            "2022-01-01,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD"
        )

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(csv_path)

    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message


def test_csv_header_detection_with_quantity_field(tmp_path):
    """Test detection of header row when first row contains 'quantity' field.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    csv_path = tmp_path / "header.csv"
    with open(csv_path, "w") as f:
        header = (
            "quantity,description,ticker,action,date,price,"
            "commission,currency\n"
        )
        data = ("100,Buy AAPL,AAPL,BUY,2022-01-01,150.00,9.99,USD")
        f.write(header + data)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(csv_path)

    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message


def test_csv_header_detection_with_dates_field(tmp_path):
    """Test detection of header row when first row contains 'dates' field.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    csv_path = tmp_path / "header.csv"
    with open(csv_path, "w") as f:
        header = (
            "dates,description,ticker,action,quantity,price,"
            "commission,currency\n"
        )
        data = ("2022-01-01,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD")
        f.write(header + data)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(csv_path)

    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message


def test_csv_header_detection_with_transaction_date_field(tmp_path):
    """Test detection of header row when first row contains 'transaction_date'.

    This test verifies that the appropriate error is raised when the first
    row appears to be a header row.
    """
    csv_path = tmp_path / "header.csv"
    with open(csv_path, "w") as f:
        header = (
            "transaction_date,description,ticker,action,quantity,"
            "price,commission,currency\n"
        )
        data = ("2022-01-01,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD")
        f.write(header + data)

    with pytest.raises(ClickException) as excinfo:
        TransactionsReader.get_transactions(csv_path)

    assert ("First row appears to be a header row" in excinfo.value.message)
    assert (
        "should contain only transaction data without headers"
        in excinfo.value.message
    )
    expected_format = (
        "YYYY-MM-DD,description,ticker,action,quantity,price,"
        "commission,currency"
    )
    assert expected_format in excinfo.value.message
