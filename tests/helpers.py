import os
import csv
import stat


def create_csv_file(directory, filename, data=None, is_readable=True):
    path = str(directory.join(filename))

    if data:
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in data:
                writer.writerow(row)

    if not is_readable:
        open(path, 'a').close()
        # set all write and execute permissions
        # to true and read permissions to false (333)
        os.chmod(path,
                 stat.S_IWUSR |
                 stat.S_IXUSR |
                 stat.S_IWGRP |
                 stat.S_IXGRP |
                 stat.S_IWOTH |
                 stat.S_IXOTH)

    return path


def transactions_to_list(transactions):
    transactions_list = []
    for t in transactions:
        transactions_list.append([
            t.date, t.description, t.ticker, t.action, t.qty, t.price,
            t.commission, t.currency
        ])
    return transactions_list
