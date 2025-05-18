import os
import csv
import json
import stat
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


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
        os.chmod(
            path,
            stat.S_IWUSR | stat.S_IXUSR | stat.S_IWGRP | stat.S_IXGRP
            | stat.S_IWOTH | stat.S_IXOTH
        )

    return path


def create_json_file(directory, filename, data=None, is_readable=True):
    """Create a JSON file with transaction data.

    Args:
        directory: The directory to create the file in
        filename: The name of the file to create
        data: List of transaction data to write
        is_readable: Whether the file should be readable

    Returns:
        The path to the created file
    """
    path = str(directory.join(filename))

    if data:
        json_data = []
        for row in data:
            # Convert CSV-style row to JSON object
            json_obj = {
                "date": row[0].strftime('%Y-%m-%d')
                if hasattr(row[0], 'strftime') else row[0],
                "description": row[1],
                "ticker": row[2],
                "action": row[3],
                "qty": str(row[4]) if isinstance(row[4], Decimal) else row[4],
                "price": str(row[5])
                if isinstance(row[5], Decimal) else row[5],
                "commission": str(row[6])
                if isinstance(row[6], Decimal) else row[6],
                "currency": row[7]
            }
            # Add any extra columns
            if len(row) > 8:
                for i, value in enumerate(row[8:], start=8):
                    json_obj[f"extra_field_{i}"] = value
            json_data.append(json_obj)

        with open(path, 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, cls=DecimalEncoder)

    if not is_readable:
        open(path, 'a').close()
        # set all write and execute permissions
        # to true and read permissions to false (333)
        os.chmod(
            path,
            stat.S_IWUSR | stat.S_IXUSR | stat.S_IWGRP | stat.S_IXGRP
            | stat.S_IWOTH | stat.S_IXOTH
        )

    return path


def transactions_to_list(transactions):
    transactions_list = []
    for t in transactions:
        transactions_list.append(
            [
                t.date,
                t.description,
                t.ticker,
                t.action,
                t.qty,
                t.price,
                t.commission,
                t.currency
            ]
        )
    return transactions_list
