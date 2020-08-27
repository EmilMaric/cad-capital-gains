from datetime import date
from capgains.transaction import Transaction


def test_transactions_to_dict(transactions):
    trans_dict = transactions[0].to_dict()

    assert trans_dict['date'] == date(2018, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 21
    assert trans_dict['price'] == 307.96
    assert trans_dict['commission'] == 20.99

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_show


def test_transactions_to_dict_calculated_partially_populated(transactions):
    trans_dict = transactions[0].to_dict(calculated_values=True)

    assert trans_dict['date'] == date(2018, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 21
    assert trans_dict['price'] == 307.96
    assert trans_dict['commission'] == 20.99
    assert trans_dict['share_balance'] is None
    assert trans_dict['proceeds'] is None
    assert trans_dict['capital_gain'] is None
    assert trans_dict['acb_delta'] is None
    assert trans_dict['acb'] is None

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_all


def test_transactions_to_dict_calculated_fully_populated(transactions):
    transactions[0].share_balance = 21
    transactions[0].proceeds = 50.05
    transactions[0].capital_gain = 64.15
    transactions[0].acb_delta = 16.23
    transactions[0].acb = 26.74

    trans_dict = transactions[0].to_dict(calculated_values=True)

    assert trans_dict['date'] == date(2018, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 21
    assert trans_dict['price'] == 307.96
    assert trans_dict['commission'] == 20.99
    assert trans_dict['share_balance'] == 21
    assert trans_dict['proceeds'] == 50.05
    assert trans_dict['capital_gain'] == 64.15
    assert trans_dict['acb_delta'] == 16.23
    assert trans_dict['acb'] == 26.74

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_all


def test_transactions_to_list(transactions):
    trans_list = transactions[0].to_list()

    assert trans_list[0] == date(2018, 2, 15)
    assert trans_list[1] == 'ESPP PURCHASE'
    assert trans_list[2] == 'ANET'
    assert trans_list[3] == 'BUY'
    assert trans_list[4] == 21
    assert trans_list[5] == 307.96
    assert trans_list[6] == 20.99

    # check that no extra values were added
    assert len(trans_list) == Transaction.num_vals_show


def test_transactions_to_list_calculated_partially_populated(transactions):
    trans_list = transactions[0].to_list(calculated_values=True)

    assert trans_list[0] == date(2018, 2, 15)
    assert trans_list[1] == 'ESPP PURCHASE'
    assert trans_list[2] == 'ANET'
    assert trans_list[3] == 'BUY'
    assert trans_list[4] == 21
    assert trans_list[5] == 307.96
    assert trans_list[6] == 20.99
    assert trans_list[7] is None
    assert trans_list[8] is None
    assert trans_list[9] is None
    assert trans_list[10] is None
    assert trans_list[11] is None

    # check that no extra values were added
    assert len(trans_list) == Transaction.num_vals_all


def test_transactions_to_list_calculated_fully_populated(transactions):
    transactions[0].share_balance = 21
    transactions[0].proceeds = 50.05
    transactions[0].capital_gain = 64.15
    transactions[0].acb_delta = 16.23
    transactions[0].acb = 26.74

    trans_list = transactions[0].to_list(calculated_values=True)

    assert trans_list[0] == date(2018, 2, 15)
    assert trans_list[1] == 'ESPP PURCHASE'
    assert trans_list[2] == 'ANET'
    assert trans_list[3] == 'BUY'
    assert trans_list[4] == 21
    assert trans_list[5] == 307.96
    assert trans_list[6] == 20.99
    assert trans_list[7] == 21
    assert trans_list[8] == 50.05
    assert trans_list[9] == 64.15
    assert trans_list[10] == 16.23
    assert trans_list[11] == 26.74

    # check that no extra values were added
    assert len(trans_list) == Transaction.num_vals_all
