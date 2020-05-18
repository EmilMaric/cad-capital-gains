import csv
from click import ClickException

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
            with open(csv_file) as f:
                reader = csv.DictReader(f)
                for entry_no, entry in enumerate(reader):
                    num_columns = len(entry)
                    if num_columns != Transaction.num_vals:
                        # Each line in the CSV file should have the same number
                        # of columns as we expect
                        raise ClickException(
                            "transaction entry {}: expected {} columns, "
                            "entry has {}".format(entry_no,
                                                  Transaction.num_vals,
                                                  num_columns))
                transaction = Transaction(*entry)
                transactions.append(transaction)
            return transactions
        except FileNotFoundError:
            raise ClickException("File not found: {}".format(csv_file))
        except OSError:
            raise OSError("Could not open {} for reading".format(csv_file))
