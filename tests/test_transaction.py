from datetime import date
from capgains.transaction import Transaction


def test_transactions_to_dict(transactions):
    trans_dict = transactions[0].to_dict()

    assert trans_dict['date'] == date(2017, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 100
    assert trans_dict['price'] == 50.00
    assert trans_dict['commission'] == 10.00

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_show


def test_transactions_to_dict_calculated_partially_populated(transactions):
    trans_dict = transactions[0].to_dict(calculated_values=True)

    assert trans_dict['date'] == date(2017, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 100
    assert trans_dict['price'] == 50.00
    assert trans_dict['commission'] == 10.00
    assert trans_dict['share_balance'] is None
    assert trans_dict['proceeds'] is None
    assert trans_dict['capital_gain'] is None
    assert trans_dict['acb_delta'] is None
    assert trans_dict['acb'] is None

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_all


def test_transactions_to_dict_calculated_fully_populated(transactions):
    transactions[0].share_balance = 50
    transactions[0].proceeds = 5000.00
    transactions[0].capital_gain = 5010.00
    transactions[0].acb_delta = 6000.00
    transactions[0].acb = 4000.00

    trans_dict = transactions[0].to_dict(calculated_values=True)

    assert trans_dict['date'] == date(2017, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 100
    assert trans_dict['price'] == 50.00
    assert trans_dict['commission'] == 10.00
    assert trans_dict['share_balance'] == 50
    assert trans_dict['proceeds'] == 5000.00
    assert trans_dict['capital_gain'] == 5010.00
    assert trans_dict['acb_delta'] == 6000.00
    assert trans_dict['acb'] == 4000.00

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_all
