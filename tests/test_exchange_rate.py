from datetime import date, timedelta
from capgains.exchange_rate import ExchangeRate
import pytest
from click import ClickException
import requests_mock as rm


@pytest.fixture(scope='function')
def USD_exchange_rates(requests_mock):
    requests_mock.get(rm.ANY,
                      json={
                        "observations": [
                            {
                                "d": "2020-05-22",
                                "FXUSDCAD": {
                                    "v": "1.2"
                                }
                            }
                        ]})
    return ExchangeRate('USD',
                        ExchangeRate.min_date,
                        date.today())


def test_exchange_rate_end_after_start():
    with pytest.raises(ClickException):
        end = date(2020, 5, 22)
        start = end + timedelta(days=1)
        ExchangeRate('USD', start, end)


def test_exchange_rate_non_existent_currency(requests_mock):
    fakeCurrency = 'IMAGINARYMONEY'
    start_date = ExchangeRate.min_date
    end_date = ExchangeRate.min_date

    requests_mock.get(rm.ANY, json={})

    with pytest.raises(ClickException):
        ExchangeRate(fakeCurrency, start_date, end_date)


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
    assert USD_exchange_rates.get_rate(friday) == 1.2


def test_exchange_rate_weekend_date(USD_exchange_rates):
    # set the date on a Sunday, expect fridays rate
    friday = date(2020, 5, 22)
    expected_rate = USD_exchange_rates.get_rate(friday)
    sunday = date(2020, 5, 24)
    assert USD_exchange_rates.get_rate(sunday) == expected_rate
