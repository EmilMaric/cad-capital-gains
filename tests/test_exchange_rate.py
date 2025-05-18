import pytest
import re
import requests_mock as rm
import requests

from datetime import date, timedelta, datetime
from decimal import Decimal
from click import ClickException

from capgains.exchange_rate import ExchangeRate


def _request_error_throwing_test(
    requests_mock, expected_error, expected_message
):
    requests_mock.get(rm.ANY, exc=expected_error)
    day = date(2020, 5, 22)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate("USD", day, day)
    assert expected_message == excinfo.value.message


@pytest.fixture(scope='function')
def USD_exchange_rates_mock(requests_mock):
    noon_rate_matcher = re.compile(ExchangeRate.valet_obs_url)
    indicative_rate_matcher = re.compile(ExchangeRate.valet_obs_url + '/FX')
    requests_mock.get(
        noon_rate_matcher,
        json={
            "observations": [
                {
                    "d": "2016-05-21", "IEXE0101": {
                        "v": "1.1"
                    }
                },
            ]
        }
    )
    requests_mock.get(
        indicative_rate_matcher,
        json={
            "observations": [
                {
                    "d": "2020-05-21", "FXUSDCAD": {
                        "v": "1.2"
                    }
                },
                {
                    "d": "2020-05-22", "FXUSDCAD": {
                        "v": "1.3"
                    }
                },
                {
                    "d": "2020-05-25", "FXUSDCAD": {
                        "v": "1.4"
                    }
                },
            ]
        }
    )


def test_exchange_rate_end_after_start():
    end = date(2020, 5, 22)
    start = end + timedelta(days=1)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate('USD', start, end)
    assert excinfo.value.message == "End date must be after start date"


def test_exchange_rate_init_before_min_date():
    early = date(2007, 4, 30)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate('USD', early, early)
    assert (
        excinfo.value.message ==
        "We do not support having transactions before 2007-05-01"
    )


def test_exchange_rate_after_max_date():
    """Test that we throw an error when we request exchange rates after the
    maximum date (which is today's date)"""
    today = datetime.today().date()
    tmr = today + timedelta(days=1)
    with pytest.raises(ClickException) as excinfo:
        ExchangeRate('USD', today, tmr)
    assert (
        excinfo.value.message ==
        "We do not support having transactions past today's date"
    )


def test_exchange_rate_ok_date(USD_exchange_rates_mock):
    # set the date on a Friday
    thursday = date(2020, 5, 21)
    friday = date(2020, 5, 22)
    er = ExchangeRate('USD', thursday, friday)
    assert er.get_rate(friday) == Decimal('1.3')


def test_exchange_rate_weekend_date(USD_exchange_rates_mock):
    # set the date on a Sunday, expect fridays rate
    friday = date(2020, 5, 22)
    sunday = date(2020, 5, 24)
    er = ExchangeRate('USD', friday, sunday)
    expected_rate = er.get_rate(friday)
    assert er.get_rate(sunday) == expected_rate


def test_exchange_rate_noon_only(USD_exchange_rates_mock):
    noon_rate_date = date(2016, 5, 21)
    er = ExchangeRate('USD', noon_rate_date, noon_rate_date)
    expected_rate = er.get_rate(noon_rate_date)
    assert expected_rate == Decimal('1.1')


def test_exchange_rate_noon_and_indicative(USD_exchange_rates_mock):
    noon_rate_date = date(2016, 5, 21)
    indicative_rate_date = date(2020, 5, 22)
    er = ExchangeRate('USD', noon_rate_date, indicative_rate_date)
    assert er.get_rate(noon_rate_date) == Decimal('1.1')
    assert er.get_rate(indicative_rate_date) == Decimal('1.3')


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
    _request_error_throwing_test(
        requests_mock,
        requests.ConnectionError,
        "Error with internet connection to URL "
        "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json : "
    )


def test_http_error_exception(requests_mock):
    _request_error_throwing_test(
        requests_mock,
        requests.HTTPError,
        "HTTP request for URL "
        "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json "
        "was unsuccessful : "
    )


def test_timeout_exception(requests_mock):
    _request_error_throwing_test(
        requests_mock,
        requests.exceptions.Timeout,
        "Request timeout on URL "
        "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json : "
    )


def test_too_many_redirects_exception(requests_mock):
    _request_error_throwing_test(
        requests_mock,
        requests.exceptions.TooManyRedirects,
        "URL https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json "
        "was bad : "
    )


def test_request_exception(requests_mock):
    _request_error_throwing_test(
        requests_mock,
        requests.exceptions.RequestException,
        "Error retrieving exchange rate from Bank of Canada API"
    )


def test_get_rate_before_min_date_exception(USD_exchange_rates_mock):
    er = ExchangeRate('USD', date(2020, 5, 22), date(2020, 5, 25))
    with pytest.raises(ClickException) as excinfo:
        er.get_rate(date(2017, 1, 2))
    error_msg = (
        "Could not find exchange rate for 2017-01-02. No rates available."
    )
    assert excinfo.value.message == error_msg


def test_exchange_rate_noon_rate_fallback(requests_mock):
    """Test fallback to noon rates when indicative rates are not available."""
    # Mock the indicative rate request to return no data
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
        json={"observations": []}
    )

    # Mock the noon rate request to return data
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/IEXE0101/json",
        json={
            "observations": [{
                "d": "2016-12-30", "IEXE0101": {
                    "v": "1.3427"
                }
            }]
        }
    )

    # Test that we get the noon rate
    rate = ExchangeRate.get_exchange_rate(date(2016, 12, 30))
    assert rate == Decimal("1.3427")


def test_exchange_rate_no_rates(requests_mock):
    """Test handling when no exchange rates are available."""
    # Mock both requests to return no data
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
        json={"observations": []}
    )
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/IEXE0101/json",
        json={"observations": []}
    )

    # Test that we get an error
    with pytest.raises(ClickException,
                       match=("Could not find exchange rate for 2016-12-30. "
                              "No rates available.")):
        ExchangeRate.get_exchange_rate(date(2016, 12, 30))


def test_exchange_rate_invalid_response(requests_mock):
    """Test handling of invalid response from Bank of Canada API."""
    # Mock both requests to return invalid JSON
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json", text="invalid json"
    )
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/IEXE0101/json", text="invalid json"
    )

    # Test that we get an error
    with pytest.raises(
            ClickException,
            match=("Error retrieving exchange rate from Bank of Canada API")):
        ExchangeRate.get_exchange_rate(date(2016, 12, 30))


def test_exchange_rate_invalid_date_format(requests_mock):
    """Test handling of invalid date format in response."""
    # Mock both requests to return invalid date format
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
        json={
            "observations": [
                {
                    "d": "invalid date", "FXUSDCAD": {
                        "v": "1.3427"
                    }
                }
            ]
        }
    )
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/IEXE0101/json",
        json={
            "observations": [
                {
                    "d": "invalid date", "IEXE0101": {
                        "v": "1.3427"
                    }
                }
            ]
        }
    )

    # Test that we get an error
    with pytest.raises(
            ClickException,
            match=("Error parsing exchange rate from Bank of Canada API")):
        ExchangeRate.get_exchange_rate(date(2016, 12, 30))


def test_exchange_rate_invalid_rate_format(requests_mock):
    """Test handling of invalid rate format in response."""
    # Mock both requests to return invalid rate format
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
        json={
            "observations": [
                {
                    "d": "2016-12-30", "FXUSDCAD": {
                        "v": "not a number"
                    }
                }
            ]
        }
    )
    requests_mock.get(
        f"{ExchangeRate.valet_obs_url}/IEXE0101/json",
        json={
            "observations": [
                {
                    "d": "2016-12-30", "IEXE0101": {
                        "v": "not a number"
                    }
                }
            ]
        }
    )

    # Test that we get an error
    with pytest.raises(
            ClickException,
            match=("Error parsing exchange rate from Bank of Canada API")):
        ExchangeRate.get_exchange_rate(date(2016, 12, 30))
