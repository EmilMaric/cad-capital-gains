import capgains.commands.capgains_show as CapGainsShow
import pytest
import mongomock
import datetime
import textwrap


@pytest.fixture()
def db():
    return mongomock.MongoClient().db


def test_show_capgains_table_default(db, capfd):
    col = db.collection

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

    for obj in objects:
        col.insert_one(obj)

    CapGainsShow.show_capgains_table(col)

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-15   ANET    ESPP PURCHASE    BUY        21  307.96             21             0
    1 2018-02-20   ANET         RSU VEST    BUY        42  249.55             63             0
    """)  # noqa: E501


def test_show_capgains_table_ticker(db, capfd):
    col = db.collection

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
                    ticker='GOOG',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    for obj in objects:
        col.insert_one(obj)

    CapGainsShow.show_capgains_table(col, ['ANET'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-15   ANET    ESPP PURCHASE    BUY        21  307.96             21             0
    """)  # noqa: E501


def test_show_capgains_table_unknown_ticker(db, capfd):
    col = db.collection

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
                    ticker='GOOG',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    for obj in objects:
        col.insert_one(obj)

    CapGainsShow.show_capgains_table(col, ['FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)  # noqa: E501


def test_show_capgains_table_known_and_unknown_ticker(db, capfd):
    col = db.collection

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
                    ticker='GOOG',
                    date=datetime.datetime(2018, 2, 20),
                    transaction_type='RSU VEST',
                    action='BUY',
                    quantity=42,
                    price=249.55,
                    share_balance=63,
                    capital_gain=0)]

    for obj in objects:
        col.insert_one(obj)

    CapGainsShow.show_capgains_table(col, ['GOOG', 'FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
            date ticker transaction_type action  quantity   price  share_balance  capital_gain
    0 2018-02-20   GOOG         RSU VEST    BUY        42  249.55             63             0
    """)  # noqa: E501


def test_show_capgains_table_empty_db(db, capfd):
    col = db.collection

    objects = []

    for obj in objects:
        col.insert_one(obj)

    CapGainsShow.show_capgains_table(col, ['ANET', 'GOOG', 'FB'])

    out, err = capfd.readouterr()

    assert out == textwrap.dedent("""\
    No results found
    """)  # noqa: E501
