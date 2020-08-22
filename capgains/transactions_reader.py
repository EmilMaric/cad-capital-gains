import csv
from click import ClickException
from datetime import datetime

from .transaction import Transaction


class TransactionsReader:
    """An interface that converts a CSV-file with transaction entries into a
    list of Transactions.
    """

    @staticmethod
    def get_transactions(csv_file):
        """Convert the CSV-file entries into a list of Transactions."""
        transactions = []
        try:
            with open(csv_file, newline='') as f:
                reader = csv.reader(f)
                last_date = None
                for entry_no, entry in enumerate(reader):
                    num_columns = len(entry)
                    if num_columns != Transaction.num_vals_show:
                        # Each line in the CSV file should have the same number
                        # of columns as we expect
                        raise ClickException(
                            "Transaction entry {}: expected {} columns, entry has {}"  # noqa: E501
                            .format(entry_no,
                                    Transaction.num_vals_show,
                                    num_columns))
                    date_str = entry[Transaction.date_idx]
                    try:
                        entry[Transaction.date_idx] = datetime.strptime(
                            date_str.split(" ")[0],
                            '%Y-%m-%d').date()
                    except ValueError:
                        raise ClickException(
                            "The date ({}) was not entered in the correct format (YYYY-MM-DD)"  # noqa: E501
                            .format(date_str))
                    qty_str = entry[Transaction.qty_idx]
                    try:
                        entry[Transaction.qty_idx] = int(qty_str)
                    except ValueError:
                        raise ClickException(
                            "The quanitity entered {} is not an integer"
                            .format(qty_str))
                    price_str = entry[Transaction.price_idx]
                    try:
                        entry[Transaction.price_idx] = float(price_str)
                    except ValueError:
                        raise ClickException(
                            "The price entered {} is not a float value"
                            .format(price_str))
                    commission_str = entry[Transaction.commission_idx]
                    try:
                        entry[Transaction.commission_idx] = \
                            float(commission_str)
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
            return transactions
        except FileNotFoundError:
            raise ClickException("File not found: {}".format(csv_file))
        except OSError:
            raise OSError("Could not open {} for reading".format(csv_file))
