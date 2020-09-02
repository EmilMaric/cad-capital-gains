from datetime import date, timedelta
import pytest
from click import ClickException
import requests_mock as rm
import requests

from capgains.exchange_rate import ExchangeRate


def _request_error_throwing_test(requests_mock, expected_error,
                                 expected_message):
    requests_mock.get(rm.ANY, exc=expected_error)
    day = date(2020, 5, 22)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate("USD", day, day)
    assert expected_message == excinfo.value.message


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
    end = date(2020, 5, 22)
    start = end + timedelta(days=1)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate('USD', start, end)
    assert excinfo.value.message == "End date must be after start date"


def test_exchange_rate_init_before_min_date():
    early = date(2017, 1, 2)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate('USD', early, early)
    assert excinfo.value.message == "Start date is before minimum date 2017-01-03"  # noqa: E501


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
    day = date(2020, 5, 22)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate("BLAHBLAH", day, day)
    assert excinfo.value.message == "Currency (BLAHBLAH) is not currently supported. The supported currencies are ['CAD', 'USD']"  # noqa: E501


def test_no_observations_found_exception(requests_mock):
    day = date(2020, 5, 22)
    requests_mock.get(rm.ANY, json={})
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate("USD", day, day)
    assert excinfo.value.message == "No observations were found using currency USD"  # noqa: E501


def test_connection_error_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.ConnectionError,
                                 "Error with internet connection to URL https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json : ")  # noqa: E501


def test_http_error_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.HTTPError,
                                 "HTTP request for URL https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json was unsuccessful : ")  # noqa: E501


def test_timeout_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.exceptions.Timeout,
                                 "Request timeout on URL https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json : ")  # noqa: E501


def test_too_many_redirects_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.exceptions.TooManyRedirects,
                                 "URL https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json was bad : ")  # noqa: E501


def test_request_exception(requests_mock):
    _request_error_throwing_test(requests_mock,
                                 requests.exceptions.RequestException,
                                 "Catastrophic error with URL https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json : ")  # noqa: E501


def test_get_rate_before_min_date_exception(USD_exchange_rates_mock):
    er = ExchangeRate('USD', date(2020, 5, 22), date(2020, 5, 25))
    with pytest.raises(ClickException) as excinfo:
        er.get_rate(date(2017, 1, 2))
    assert excinfo.value.message == "Unable to find exchange rate on 2017-01-02"  # noqa: E501
