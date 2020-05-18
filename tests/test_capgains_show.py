import capgains.commands.capgains_show as CapGainsShow
import datetime
import textwrap


def test_show_capgains_table_default(capfd):
    objects = [dict(id=0,
                    ticker='ANET',
                    date=datetime.datetime(2018, 2, 15),
                    transaction_type='ESPP PURCHASE',
                    action='BUY',
                    quantity=21,
                    price=307.96,
                    share_balance=21,
                    capital_gain=0),

               dict(id=1,
                    ticker='ANET',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    CapGainsShow.show_capgains_table(objects)

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-15   ANET    ESPP PURCHASE    BUY        21  307.96             21             0
    1 2018-02-20   ANET         RSU VEST    BUY        42  249.55             63             0
    """)  # noqa: E501


def test_show_capgains_table_both_tickers(capfd):
    objects = [dict(id=0,
                    ticker='ANET',
                    date=datetime.datetime(2018, 2, 15),
                    transaction_type='ESPP PURCHASE',
                    action='BUY',
                    quantity=21,
                    price=307.96,
                    share_balance=21,
                    capital_gain=0),

               dict(id=1,
                    ticker='GOOGL',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    CapGainsShow.show_capgains_table(objects, ['ANET', 'GOOGL'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-15   ANET    ESPP PURCHASE    BUY        21  307.96             21             0
    1 2018-02-20  GOOGL         RSU VEST    BUY        42  249.55             63             0
    """)  # noqa: E501


def test_show_capgains_table_one_ticker(capfd):
    objects = [dict(id=0,
                    ticker='ANET',
                    date=datetime.datetime(2018, 2, 15),
                    transaction_type='ESPP PURCHASE',
                    action='BUY',
                    quantity=21,
                    price=307.96,
                    share_balance=21,
                    capital_gain=0),

               dict(id=1,
                    ticker='GOOGL',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    CapGainsShow.show_capgains_table(objects, ['ANET'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-15   ANET    ESPP PURCHASE    BUY        21  307.96             21             0
    """)  # noqa: E501


def test_show_capgains_table_unknown_ticker(capfd):
    objects = [dict(id=0,
                    ticker='ANET',
                    date=datetime.datetime(2018, 2, 15),
                    transaction_type='ESPP PURCHASE',
                    action='BUY',
                    quantity=21,
                    price=307.96,
                    share_balance=21,
                    capital_gain=0),

               dict(id=1,
                    ticker='GOOGL',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    CapGainsShow.show_capgains_table(objects, ['FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)  # noqa: E501


def test_show_capgains_table_known_and_unknown_ticker(capfd):
    objects = [dict(id=0,
                    ticker='ANET',
                    date=datetime.datetime(2018, 2, 15),
                    transaction_type='ESPP PURCHASE',
                    action='BUY',
                    quantity=21,
                    price=307.96,
                    share_balance=21,
                    capital_gain=0),

               dict(id=1,
                    ticker='GOOGL',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    CapGainsShow.show_capgains_table(objects, ['GOOGL', 'FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-20  GOOGL         RSU VEST    BUY        42  249.55             63             0
    """)  # noqa: E501


def test_show_capgains_table_empty_input(capfd):
    objects = []

    CapGainsShow.show_capgains_table(objects, ['ANET', 'GOOGL', 'FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)  # noqa: E501
