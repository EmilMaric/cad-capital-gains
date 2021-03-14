import pytest


def test_cannot_set_negative_share_balance(transactions):
    with pytest.raises(ValueError) as excinfo:
        transactions[0].share_balance = -1
    assert str(excinfo.value) == "Share balance cannot be negative"
