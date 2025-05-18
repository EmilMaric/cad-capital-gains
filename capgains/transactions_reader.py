import csv
import json
from click import ClickException
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

from .transaction import Transaction
from .transactions import Transactions


class TransactionsReader:
    """An interface that converts a CSV or JSON file with transaction entries
    into a list of txs."""
    columns = [
        "date",
        "description",
        "ticker",
        "action",
        "qty",
        "price",
        "commission",
        "currency"
    ]

    @classmethod
    def get_transactions(cls, input_file):
        """Convert the input file entries into a list of txs.

        Supports both CSV and JSON formats based on file extension.
        """
        try:
            _, ext = os.path.splitext(input_file)
            if ext.lower() == '.json':
                return cls._get_transactions_from_json(input_file)
            else:  # Default to CSV for all other extensions
                return cls._get_transactions_from_csv(input_file)
        except FileNotFoundError:
            msg = f"File not found: {input_file}"
            raise ClickException(msg)
        except OSError:
            msg = f"Could not open {input_file} for reading"
            raise OSError(msg)

    @classmethod
    def _get_transactions_from_json(cls, json_file):
        """Convert JSON file entries into a list of txs."""
        transactions = []
        last_date = None

        with open(json_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                msg = f"Invalid JSON format in file: {json_file}"
                raise ClickException(msg)

            if not isinstance(data, list):
                msg = "JSON file must contain a list of txs"
                raise ClickException(msg)

            for entry_no, entry in enumerate(data):
                # Check for extra fields
                extra_fields = [
                    field for field in entry if field not in cls.columns
                ]
                if extra_fields:
                    fmt = (
                        "Transaction entry {}: expected {} columns, "
                        "entry has {}"
                    )
                    msg = fmt.format(entry_no, len(cls.columns), len(entry))
                    raise ClickException(msg)

                # Validate required fields
                missing_fields = [
                    field for field in cls.columns if field not in entry
                ]
                if missing_fields:
                    msg = (
                        f"Transaction entry {entry_no}: missing required "
                        f"fields: {', '.join(missing_fields)}"
                    )
                    raise ClickException(msg)

                # Parse date
                try:
                    date_str = entry["date"]
                    date = datetime.strptime(
                        date_str.split(" ")[0], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    msg = (
                        f"The date ({date_str}) was not entered in the "
                        "correct format (YYYY-MM-DD)"
                    )
                    raise ClickException(msg)

                # Parse numeric fields
                try:
                    qty = Decimal(str(entry["qty"]))
                except (InvalidOperation, TypeError):
                    msg = (
                        f"The quantity entered {entry['qty']} "
                        "is not a valid number"
                    )
                    raise ClickException(msg)

                try:
                    price = Decimal(str(entry["price"]))
                except (InvalidOperation, TypeError):
                    msg = (
                        f"The price entered {entry['price']} "
                        "is not a valid number"
                    )
                    raise ClickException(msg)

                try:
                    commission = Decimal(str(entry["commission"]))
                except (InvalidOperation, TypeError):
                    msg = (
                        f"The commission entered {entry['commission']} "
                        "is not a valid number"
                    )
                    raise ClickException(msg)

                # Create transaction
                transaction = Transaction(
                    date,
                    entry["description"],
                    entry["ticker"],
                    entry["action"],
                    qty,
                    price,
                    commission,
                    entry["currency"]
                )

                # Check chronological order
                if last_date and transaction.date < last_date:
                    msg = "Transactions are not in chronological order"
                    raise ClickException(msg)
                last_date = transaction.date
                transactions.append(transaction)

        return Transactions(transactions)

    @classmethod
    def _get_transactions_from_csv(cls, csv_file):
        """Convert CSV file entries into a list of txs."""
        transactions = []
        with open(csv_file, newline='') as f:
            reader = csv.reader(f)
            last_date = None
            for entry_no, entry in enumerate(reader):
                # Strip whitespace from all fields
                entry = [field.strip() for field in entry]

                # Skip empty rows
                if not any(entry):
                    continue

                actual_num_columns = len(entry)
                expected_num_columns = len(cls.columns)
                if actual_num_columns != expected_num_columns:
                    # Each line in the CSV file should have the same number
                    # of columns as we expect
                    fmt = (
                        "Transaction entry {}: expected {} columns, "
                        "entry has {}"
                    )
                    msg = fmt.format(
                        entry_no, expected_num_columns, actual_num_columns
                    )
                    raise ClickException(msg)

                # Check for potential header row
                if entry_no == 0:
                    potential_headers = [field.lower() for field in entry]
                    header_fields = [
                        'date',
                        'description',
                        'ticker',
                        'action',
                        'quantity',
                        'qty',
                        'price'
                    ]
                    header_match = any(
                        col in potential_headers for col in header_fields
                    )
                    if header_match:
                        fmt = (
                            "First row appears to be a header row. The "
                            "CSV file should contain only transaction data "
                            "without headers.\nEach row should be in the "
                            "format: YYYY-MM-DD,description,ticker,action,"
                            "quantity,price,commission,currency"
                        )
                        raise ClickException(fmt)

                date_idx = cls.columns.index("date")
                date_str = entry[date_idx]
                try:
                    entry[date_idx] = datetime.strptime(
                        date_str.split(" ")[0], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    if entry_no == 0:
                        # If first row and date parsing failed, check if header
                        header_values = ['date', 'dates', 'transaction date']
                        if date_str.lower() in header_values:
                            fmt = (
                                "First row appears to be a header row. "
                                "The CSV file should contain only "
                                "transaction data without headers.\n"
                                "Each row should be in the format: "
                                "YYYY-MM-DD,description,ticker,action,"
                                "quantity,price,commission,currency"
                            )
                            raise ClickException(fmt)
                    msg = (
                        f"The date ({date_str}) was not entered in the "
                        "correct format (YYYY-MM-DD)"
                    )
                    raise ClickException(msg)

                qty_idx = cls.columns.index("qty")
                qty_str = entry[qty_idx]
                try:
                    entry[qty_idx] = Decimal(qty_str)
                except InvalidOperation:
                    msg = (
                        f"The quantity entered {qty_str} "
                        "is not a valid number"
                    )
                    raise ClickException(msg)

                price_idx = cls.columns.index("price")
                price_str = entry[price_idx]
                try:
                    entry[price_idx] = Decimal(price_str)
                except InvalidOperation:
                    msg = (
                        f"The price entered {price_str} "
                        "is not a valid number"
                    )
                    raise ClickException(msg)

                commission_idx = cls.columns.index("commission")
                commission_str = entry[commission_idx]
                try:
                    entry[commission_idx] = Decimal(commission_str)
                except InvalidOperation:
                    msg = (
                        f"The commission entered {commission_str} "
                        "is not a valid number"
                    )
                    raise ClickException(msg)

                transaction = Transaction(*entry)
                if last_date and transaction.date < last_date:
                    msg = "Transactions are not in chronological order"
                    raise ClickException(msg)
                last_date = transaction.date
                transactions.append(transaction)

        return Transactions(transactions)
