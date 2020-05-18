import capgains.commands.capgains_show as CapGainsShow
from datetime import datetime as dt
import textwrap
import pytest
import csv


@pytest.fixture()
def empty_csv_file(tmpdir_factory, scope='module'):
    filename = str(tmpdir_factory.mktemp("data").join("empty.csv"))
    open(filename, 'a').close()
    return filename


@pytest.fixture()
def csv_file_and_data(tmpdir_factory, scope='module'):
    filename = str(tmpdir_factory.mktemp("data").join("data.csv"))

    objects = [dict(id=0,
                    ticker='ANET',
                    date=dt.strftime(dt(2018, 2, 15),
                                     '%Y-%m-%d'),
                    transaction_type='ESPP PURCHASE',
                    action='BUY',
                    quantity='21',
                    price='307.96',
                    share_balance='21',
                    capital_gain='0'),

               dict(id=1,
                    ticker='GOOGL',
                    date=dt.strftime(dt(2018, 2, 20),
                                     '%Y-%m-%d'),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity='42',
                    price='249.55',
                    share_balance='63',
                    capital_gain='0')]

    keys = objects[0].keys()

    with open(filename, 'w') as input_file:
        dict_writer = csv.DictWriter(input_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(objects)

    return filename, objects


def test_show_capgains_table_default(csv_file_and_data, capfd):
    filename, _ = csv_file_and_data

    CapGainsShow.show_capgains_table(filename)

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
             date ticker transaction_type action quantity   price share_balance capital_gain
    0  2018-02-15   ANET    ESPP PURCHASE    BUY       21  307.96            21            0
    1  2018-02-20  GOOGL         RSU VEST    BUY       42  249.55            63            0
    """)  # noqa: E501


def test_show_capgains_table_empty_file(empty_csv_file, capfd):
    filename = empty_csv_file

    CapGainsShow.show_capgains_table(filename)

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)


def test_show_capgains_table_file_not_found(capfd):
    filename = 'filedoesnotexist.csv'

    CapGainsShow.show_capgains_table(filename)

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    File does not exist
    """)


def test_print_data_default(csv_file_and_data, capfd):
    _, objects = csv_file_and_data

    CapGainsShow.print_data(objects)

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
             date ticker transaction_type action quantity   price share_balance capital_gain
    0  2018-02-15   ANET    ESPP PURCHASE    BUY       21  307.96            21            0
    1  2018-02-20  GOOGL         RSU VEST    BUY       42  249.55            63            0
    """)  # noqa: E501


def test_print_data_both_tickers(csv_file_and_data, capfd):
    _, objects = csv_file_and_data

    CapGainsShow.print_data(objects, ['ANET', 'GOOGL'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
             date ticker transaction_type action quantity   price share_balance capital_gain
    0  2018-02-15   ANET    ESPP PURCHASE    BUY       21  307.96            21            0
    1  2018-02-20  GOOGL         RSU VEST    BUY       42  249.55            63            0
    """)  # noqa: E501


def test_print_data_one_ticker(csv_file_and_data, capfd):
    _, objects = csv_file_and_data

    CapGainsShow.print_data(objects, ['ANET'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
             date ticker transaction_type action quantity   price share_balance capital_gain
    0  2018-02-15   ANET    ESPP PURCHASE    BUY       21  307.96            21            0
    """)  # noqa: E501


def test_print_data_unknown_ticker(csv_file_and_data, capfd):
    _, objects = csv_file_and_data

    CapGainsShow.print_data(objects, ['FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)  # noqa: E501


def test_print_data_known_and_unknown_ticker(csv_file_and_data, capfd):
    _, objects = csv_file_and_data

    CapGainsShow.print_data(objects, ['GOOGL', 'FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
             date ticker transaction_type action quantity   price share_balance capital_gain
    0  2018-02-20  GOOGL         RSU VEST    BUY       42  249.55            63            0
    """)  # noqa: E501


def test_print_data_empty_input(capfd):
    CapGainsShow.print_data([], ['ANET', 'GOOGL', 'FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)  # noqa: E501
