from click.testing import CliRunner
from capgains.cli import capgains

from tests.helpers import create_csv_file, transactions_to_list


def test_show_file_not_found(testfiles_dir):
    """Testing the capgains show command with a file that doesn't exist"""
    filepath = create_csv_file(testfiles_dir,
                               "showdnetest.csv")

    runner = CliRunner()
    result = runner.invoke(capgains, ['show', filepath])

    assert result.exit_code == 1
    assert result.output == """\
Error: File not found: {}
""".format(filepath)


def test_show_no_ticker_arg(testfiles_dir, transactions):
    """Testing the capgains show command providing no filtering argument"""
    filepath = create_csv_file(testfiles_dir,
                               "showtickertest.csv",
                               transactions_to_list(transactions),
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['show', filepath])

    assert result.exit_code == 0
    assert result.output == """\
+------------+--------------------+----------+----------+-------+---------+--------------+------------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+--------------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE      | ANET     | BUY      |   100 |   50.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST           | GOOGL    | BUY      |    30 |   20.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST           | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |
| 2019-02-15 | ESPP PURCHASE      | ANET     | BUY      |    50 |  130.00 |        10.00 |        USD |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501


def test_show_ticker_arg(testfiles_dir, transactions):
    """Testing the capgains show command with a ticker filter"""
    filepath = create_csv_file(testfiles_dir,
                               "showtickertest.csv",
                               transactions_to_list(transactions),
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['show', filepath, '-t', 'ANET'])

    assert result.exit_code == 0
    assert result.output == """\
+------------+--------------------+----------+----------+-------+---------+--------------+------------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |
|------------+--------------------+----------+----------+-------+---------+--------------+------------|
| 2017-02-15 | ESPP PURCHASE      | ANET     | BUY      |   100 |   50.00 |        10.00 |        USD |
| 2018-02-20 | RSU VEST           | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |
| 2019-02-15 | ESPP PURCHASE      | ANET     | BUY      |    50 |  130.00 |        10.00 |        USD |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+
"""  # noqa: E501


def test_calc_no_ticker_arg(testfiles_dir, transactions, exchange_rates_mock):
    """Testing the capgains calc command providing no filtering argument"""
    filepath = create_csv_file(testfiles_dir,
                               "calctickertest.csv",
                               transactions_to_list(transactions),
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', filepath, '2018'])

    assert result.exit_code == 0
    assert result.output == """\
ANET-2018
[Total Gains = 6,970.00]
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |   share_balance |   proceeds |   capital_gain |   acb_delta |      acb |
|------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------|
| 2018-02-20 | RSU VEST           | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |              50 |  11,980.00 |       6,970.00 |   -5,010.00 | 5,010.00 |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+

GOOGL-2018
No capital gains

"""  # noqa: E501


def test_calc_ticker_arg(testfiles_dir, transactions, exchange_rates_mock):
    """Testing the capgains calc command and providing a ticker"""
    filepath = create_csv_file(testfiles_dir,
                               "calctickertest.csv",
                               transactions_to_list(transactions),
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', filepath, '2018', '-t', 'ANET'])

    assert result.exit_code == 0
    assert result.output == """\
ANET-2018
[Total Gains = 6,970.00]
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+
| date       | transaction_type   | ticker   | action   |   qty |   price |   commission |   currency |   share_balance |   proceeds |   capital_gain |   acb_delta |      acb |
|------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------|
| 2018-02-20 | RSU VEST           | ANET     | SELL     |    50 |  120.00 |        10.00 |        USD |              50 |  11,980.00 |       6,970.00 |   -5,010.00 | 5,010.00 |
+------------+--------------------+----------+----------+-------+---------+--------------+------------+-----------------+------------+----------------+-------------+----------+

"""  # noqa: E501


def test_calc_no_year(testfiles_dir, transactions):
    """Testing the capgains calc command without a year"""
    filepath = create_csv_file(testfiles_dir,
                               "calctickertest.csv",
                               transactions_to_list(transactions),
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', filepath, '-t', 'ANET'])
    assert result.exit_code == 2

    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', filepath])
    assert result.exit_code == 2
