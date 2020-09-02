from datetime import date, timedelta
from capgains.exchange_rate import ExchangeRate
import pytest
from click import ClickException
import requests_mock as rm
import requests


def _request_error_throwing_test(requests_mock, expected_error):
    with pytest.raises(ClickException):
        requests_mock.get(rm.ANY,
                          exc=expected_error)
        day = date(2020, 5, 22)
        ExchangeRate("USD", day, day)


@pytest.fixture(scope='function')
def USD_exchange_rates_mock(requests_mock):
    requests_mock.get(rm.ANY,
                      json={
                        "observations": [
                            {
                                "d": "2020-05-21",
                                "FXUSDCAD": {
                                    "v": "1.2"
                                }
                            },
                            {
                                "d": "2020-05-22",
                                "FXUSDCAD": {
                                    "v": "1.3"
                                }
                            },
                            {
                                "d": "2020-05-25",
                                "FXUSDCAD": {
                                    "v": "1.4"
                                }
                            },
                        ]
                      })


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


def test_exchange_rate_ok_date(USD_exchange_rates_mock):
    # set the date on a Friday
    friday = date(2020, 5, 22)
    er = ExchangeRate('USD', ExchangeRate.min_date, date.today())
    assert er.get_rate(friday) == 1.3


def test_exchange_rate_weekend_date(USD_exchange_rates_mock):
    # set the date on a Sunday, expect fridays rate
    friday = date(2020, 5, 22)
    sunday = date(2020, 5, 24)
    er = ExchangeRate('USD', ExchangeRate.min_date, date.today())
    expected_rate = er.get_rate(friday)
    assert er.get_rate(sunday) == expected_rate


def test_cad_to_cad_rate_is_1():
    day = date(2020, 5, 22)
    er = ExchangeRate('CAD', day, day)
    assert er.get_rate(day) == 1


def test_unsupported_currency_returns_error():
    with pytest.raises(ClickException):
        day = date(2020, 5, 22)
        ExchangeRate("BLAHBLAH", day, day)


def test_no_observations_found_exception(requests_mock):
    with pytest.raises(ClickException):
        day = date(2020, 5, 22)
        requests_mock.get(rm.ANY, json={})
        ExchangeRate("USD", day, day)


def test_connection_error_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.ConnectionError)


def test_http_error_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.HTTPError)


def test_timeout_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.exceptions.Timeout)


def test_too_many_redirects_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.exceptions.TooManyRedirects)


def test_request_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.exceptions.RequestException)


def test_get_rate_before_min_date_exception(USD_exchange_rates_mock):
    with pytest.raises(ClickException):
        er = ExchangeRate('USD', date(2020, 5, 22), date(2020, 5, 25))
        er.get_rate(ExchangeRate.min_date - timedelta(days=1))
