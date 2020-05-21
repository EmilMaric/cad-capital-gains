import os
import csv


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
