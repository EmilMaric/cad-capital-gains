from capgains.transaction import Transaction


def test_transactions_to_dict(transactions):
    trans_dict = transactions[0].to_dict()

    assert trans_dict['date'] == '2018-02-15'
    assert trans_dict['transaction_type'] == 'ESPP PURCHASE'
    assert trans_dict['action'] == 'BUY'
    assert trans_dict['ticker'] == 'ANET'
    assert trans_dict['qty'] == '21'
    assert trans_dict['price'] == '307.96'
    assert trans_dict['commission'] == '20.99'

    # check that no extra values we added
    assert len(trans_dict) == Transaction.num_vals
