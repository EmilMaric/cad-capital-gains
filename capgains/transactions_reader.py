import csv
from click import ClickException
from datetime import datetime

from .transaction import Transaction
from .transactions import Transactions


class TransactionsReader:
    """An interface that converts a CSV-file with transaction entries into a
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
    def get_transactions(cls, csv_file):
        """Convert the CSV-file entries into a list of Transactions."""
        transactions = []
        try:
            with open(csv_file, newline='') as f:
                reader = csv.reader(f)
                last_date = None
                for entry_no, entry in enumerate(reader):
                    actual_num_columns = len(entry)
                    expected_num_columns = len(cls.columns)
                    if actual_num_columns != expected_num_columns:
                        # Each line in the CSV file should have the same number
                        # of columns as we expect
                        raise ClickException(
                            "Transaction entry {}: expected {} columns, entry has {}"  # noqa: E501
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
                            "The date ({}) was not entered in the correct format (YYYY-MM-DD)"  # noqa: E501
                            .format(date_str))
                    qty_idx = cls.columns.index("qty")
                    qty_str = entry[qty_idx]
                    try:
                        entry[qty_idx] = int(qty_str)
                    except ValueError:
                        raise ClickException(
                            "The quanitity entered {} is not an integer"
                            .format(qty_str))
                    price_idx = cls.columns.index("price")
                    price_str = entry[price_idx]
                    try:
                        entry[price_idx] = float(price_str)
                    except ValueError:
                        raise ClickException(
                            "The price entered {} is not a float value"
                            .format(price_str))
                    commission_idx = cls.columns.index("commission")
                    commission_str = entry[commission_idx]
                    try:
                        entry[commission_idx] = float(commission_str)
                    except ValueError:
                        raise ClickException(
                            "The commission entered {} is not a float value"
                            .format(commission_str))
                    transaction = Transaction(*entry)
                    if last_date:
                        if transaction.date < last_date:
                            raise ClickException(
                                "Transactions were not entered in chronological order")  # noqa: E501
                    last_date = transaction.date
                    transactions.append(transaction)
            return Transactions(transactions)
        except FileNotFoundError:
            raise ClickException("File not found: {}".format(csv_file))
        except OSError:
            raise OSError("Could not open {} for reading".format(csv_file))
