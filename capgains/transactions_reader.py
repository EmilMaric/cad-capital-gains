import csv
import json
from click import ClickException
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

from .transaction import Transaction
from .transactions import Transactions


class TransactionsReader:
    """An interface that converts a CSV or JSON file with transaction entries into a
    list of Transactions.
    """
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
        """Convert the input file entries into a list of Transactions.
        
        Supports both CSV and JSON formats based on file extension.
        """
        try:
            _, ext = os.path.splitext(input_file)
            if ext.lower() == '.json':
                return cls._get_transactions_from_json(input_file)
            else:  # Default to CSV for all other extensions
                return cls._get_transactions_from_csv(input_file)
        except FileNotFoundError:
            raise ClickException("File not found: {}".format(input_file))
        except OSError:
            raise OSError("Could not open {} for reading".format(input_file))

    @classmethod
    def _get_transactions_from_json(cls, json_file):
        """Convert JSON file entries into a list of Transactions."""
        transactions = []
        last_date = None

        with open(json_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                raise ClickException("Invalid JSON format in file: {}".format(json_file))

            if not isinstance(data, list):
                raise ClickException("JSON file must contain a list of transactions")

            for entry_no, entry in enumerate(data):
                # Check for extra fields
                extra_fields = [field for field in entry if field not in cls.columns]
                if extra_fields:
                    raise ClickException(
                        "Transaction entry {}: expected {} columns, entry has {}"
                        .format(entry_no, len(cls.columns), len(entry)))

                # Validate required fields
                missing_fields = [field for field in cls.columns if field not in entry]
                if missing_fields:
                    raise ClickException(
                        "Transaction entry {}: missing required fields: {}"
                        .format(entry_no, ", ".join(missing_fields)))

                # Parse date
                try:
                    date_str = entry["date"]
                    date = datetime.strptime(date_str.split(" ")[0], '%Y-%m-%d').date()
                except ValueError:
                    raise ClickException(
                        "The date ({}) was not entered in the correct format (YYYY-MM-DD)"
                        .format(date_str))

                # Parse numeric fields
                try:
                    qty = Decimal(str(entry["qty"]))
                except (InvalidOperation, TypeError):
                    raise ClickException(
                        "The quantity entered {} is not a valid number"
                        .format(entry["qty"]))

                try:
                    price = Decimal(str(entry["price"]))
                except (InvalidOperation, TypeError):
                    raise ClickException(
                        "The price entered {} is not a valid number"
                        .format(entry["price"]))

                try:
                    commission = Decimal(str(entry["commission"]))
                except (InvalidOperation, TypeError):
                    raise ClickException(
                        "The commission entered {} is not a valid number"
                        .format(entry["commission"]))

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
                    raise ClickException("Transactions were not entered in chronological order")
                last_date = transaction.date
                transactions.append(transaction)

        return Transactions(transactions)

    @classmethod
    def _get_transactions_from_csv(cls, csv_file):
        """Convert CSV file entries into a list of Transactions."""
        transactions = []
        with open(csv_file, newline='') as f:
            reader = csv.reader(f)
            last_date = None
            for entry_no, entry in enumerate(reader):
                # Strip whitespace from all fields
                entry = [field.strip() for field in entry]
                
                actual_num_columns = len(entry)
                expected_num_columns = len(cls.columns)
                if actual_num_columns != expected_num_columns:
                    # Each line in the CSV file should have the same number
                    # of columns as we expect
                    raise ClickException(
                        "Transaction entry {}: expected {} columns, entry has {}"
                        .format(entry_no,
                                expected_num_columns,
                                actual_num_columns))
                date_idx = cls.columns.index("date")
                date_str = entry[date_idx]
                try:
                    entry[date_idx] = datetime.strptime(
                        date_str.split(" ")[0],
                        '%Y-%m-%d').date()
                except ValueError:
                    raise ClickException(
                        "The date ({}) was not entered in the correct format (YYYY-MM-DD)"
                        .format(date_str))
                qty_idx = cls.columns.index("qty")
                qty_str = entry[qty_idx]
                try:
                    entry[qty_idx] = Decimal(qty_str)
                except InvalidOperation:
                    raise ClickException(
                        "The quantity entered {} is not a valid number"
                        .format(qty_str))
                price_idx = cls.columns.index("price")
                price_str = entry[price_idx]
                try:
                    entry[price_idx] = Decimal(price_str)
                except InvalidOperation:
                    raise ClickException(
                        "The price entered {} is not a valid number"
                        .format(price_str))
                commission_idx = cls.columns.index("commission")
                commission_str = entry[commission_idx]
                try:
                    entry[commission_idx] = Decimal(commission_str)
                except InvalidOperation:
                    raise ClickException(
                        "The commission entered {} is not a valid number"
                        .format(commission_str))
                transaction = Transaction(*entry)
                if last_date:
                    if transaction.date < last_date:
                        raise ClickException(
                            "Transactions were not entered in chronological order")
                last_date = transaction.date
                transactions.append(transaction)
        return Transactions(transactions)
