from click import ClickException
import os
import csv
from datetime import datetime as dt
import pytest
from capgains.transactions_reader import TransactionsReader


def create_csv_file(directory, filename, data=None, is_readable=True):
    path = str(directory.join(filename))

    if data:
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            for row in data:
                writer.writerow(row)

    if not is_readable:
        open(path, 'a').close()

        # set permissions to chmod 000
        os.chmod(path, 000)

    return path


def test_transactions_reader_default(testfiles_dir):

    filepath = create_csv_file(testfiles_dir,
                               "too_many_cols.csv",
                               [[dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
                                 'ESPP PURCHASE',
                                 'ANET',
                                 'BUY',
                                 '21',
                                 '307.96',
                                 '20.99']],
                               True)

    assert len(TransactionsReader.get_transactions(filepath)) == 1


def test_transactions_reader_columns_error(testfiles_dir):
    with pytest.raises(ClickException):
        filepath = create_csv_file(testfiles_dir,
                                   "too_many_cols.csv",
                                   [[dt.strftime(dt(2018, 2, 15), '%Y-%m-%d'),
                                     'ESPP PURCHASE',
                                     'ANET',
                                     'BUY',
                                     '21',
                                     '307.96',
                                     '20.99',
                                     'EXTRA_COLUMN_VALUE']],
                                   True)
        TransactionsReader.get_transactions(filepath)


def test_transactions_reader_file_not_found_error(testfiles_dir):
    with pytest.raises(ClickException):
        TransactionsReader.get_transactions(create_csv_file(testfiles_dir,
                                                            "dne.csv"))


def test_transactions_reader_OS_error(testfiles_dir):
    with pytest.raises(OSError):
        TransactionsReader.get_transactions(create_csv_file(testfiles_dir,
                                                            "unreadable.csv",
                                                            is_readable=False))
