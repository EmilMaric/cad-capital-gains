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
                            "transaction entry {}: expected {} columns, "
                            "entry has {}".format(entry_no,
                                                  Transaction.num_vals_show,
                                                  num_columns))

                    entry[0] = datetime.strptime(entry[0].split(" ")[0],
                                                 '%Y-%m-%d').date()
                    entry[4] = int(entry[4])
                    entry[5] = float(entry[5])
                    entry[6] = float(entry[6])
                    transaction = Transaction(*entry)
                    if last_date:
                        if transaction.date < last_date:
                            raise ClickException("Transactions were not entered in chronological order")
                    last_date = transaction.date
                    transactions.append(transaction)
            return transactions
        except FileNotFoundError:
            raise ClickException("File not found: {}".format(csv_file))
        except OSError:
            raise OSError("Could not open {} for reading".format(csv_file))
