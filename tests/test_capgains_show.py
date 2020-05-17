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
            date  quantity   price ticker
    0 2018-02-15        21  307.96   ANET
    1 2018-02-20        42  249.55   ANET
    """)
