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

def test_transactions_to_dict_calculated(transactions):
    trans_dict = transactions[0].to_dict(calculated_values=True)

    assert trans_dict['date'] == date(2018, 2, 15)
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == 21
    assert trans_dict['price'] == 307.96
    assert trans_dict['commission'] == 20.99
    assert trans_dict['share_balance'] == None
    assert trans_dict['proceeds'] == None
    assert trans_dict['capital_gain'] == None
    assert trans_dict['acb_delta'] == None
    assert trans_dict['acb'] == None

    # check that no extra values were added
    assert len(trans_dict) == Transaction.num_vals_all
