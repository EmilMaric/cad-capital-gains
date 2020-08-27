from capgains import __version__
from click.testing import CliRunner
from capgains.cli import capgains
from tests.helpers import create_csv_file


def test_version():
    assert __version__ == '0.1.0'


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


def test_show_no_ticker_arg(testfiles_dir, transactions_as_list):
    """Testing the capgains show command providing no filtering argument"""
    filepath = create_csv_file(testfiles_dir,
                               "showtickertest.csv",
                               transactions_as_list,
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['show', filepath])

    assert result.exit_code == 0
    assert result.output == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
2018-02-20  RSU VEST            GOOGL     BUY          42   249.55          0.00
"""  # noqa: E501


def test_show_ticker_arg(testfiles_dir, transactions_as_list):
    """Testing the capgains show command with a ticker filter"""
    filepath = create_csv_file(testfiles_dir,
                               "showtickertest.csv",
                               transactions_as_list,
                               True)

    runner = CliRunner()
    result = runner.invoke(capgains, ['show', filepath, '-t', 'ANET'])

    assert result.exit_code == 0
    assert result.output == """\
date        transaction_type    ticker    action      qty    price    commission
----------  ------------------  --------  --------  -----  -------  ------------
2018-02-15  ESPP PURCHASE       ANET      BUY          21   307.96         20.99
"""  # noqa: E501
