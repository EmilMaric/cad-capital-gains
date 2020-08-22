from datetime import date, timedelta
from capgains.exchange_rate import ExchangeRate
import pytest
from click import ClickException


@pytest.fixture(scope='module')
def USD_exchange_rates():
    return ExchangeRate('USD',
                        ExchangeRate.min_date,
                        date.today())


def test_exchange_rate_end_after_start():
    with pytest.raises(ClickException):
        end = date(2020, 5, 22)
        start = end + timedelta(days=1)
        ExchangeRate('USD', start, end)


def test_exchange_rate_only_weekend():
    weekend = date(2020, 5, 24)
    er = ExchangeRate('USD', weekend, weekend)
    assert len(er._rates) > 0


def test_exchange_rate_non_existent_currency():
    with pytest.raises(ClickException):
        ExchangeRate('IMAGINARYMONEY',
                     ExchangeRate.min_date,
                     ExchangeRate.min_date)


def test_exchange_rate_init_before_min_date():
    with pytest.raises(ClickException):
        early = ExchangeRate.min_date - timedelta(days=1)
        ExchangeRate('USD', early, early)


def test_exchange_rate_get_before_min_date():
    with pytest.raises(ClickException):
        early = ExchangeRate.min_date - timedelta(days=1)
        ExchangeRate('USD', early, early)


def test_exchange_rate_ok_date(USD_exchange_rates):
    # set the date on a Friday
    friday = date(2020, 5, 22)
    assert USD_exchange_rates.get_rate(friday) == 1.4015


def test_exchange_rate_weekend_date(USD_exchange_rates):
    # set the date on a Sunday, expect fridays rate
    friday = date(2020, 5, 22)
    expected_rate = USD_exchange_rates.get_rate(friday)
    sunday = date(2020, 5, 24)
    assert USD_exchange_rates.get_rate(sunday) == expected_rate
