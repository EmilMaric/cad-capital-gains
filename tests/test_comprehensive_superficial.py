from datetime import date, timedelta
from click.testing import CliRunner
import json
import os

from capgains.cli import capgains
from capgains.exchange_rate import ExchangeRate


def setup_exchange_rates_mock(requests_mock, start_date, end_date, rate='2.0'):
    """Helper function to set up exchange rate mocking for a date range."""
    # For noon rates (before 2017-01-03)
    noon_observations = []
    if start_date < date(2017, 1, 3):
        # Add noon rates from start_date to 2017-01-02
        # Account for double 7-day lookback
        current_date = start_date - timedelta(days=14)
        end_noon = min(end_date, date(2017, 1, 2))
        while current_date <= end_noon:
            noon_observations.append(
                {
                    'd': current_date.isoformat(), 'IEXE0101': {
                        'v': rate
                    }
                }
            )
            current_date += timedelta(days=1)
        requests_mock.get(
            f"{ExchangeRate.valet_obs_url}/IEXE0101/json",
            json={"observations": noon_observations}
        )

    # For indicative rates (after 2017-01-03)
    indicative_observations = []
    if end_date >= date(2017, 1, 3):
        # Add indicative rates from 2017-01-03 to end_date
        current_date = max(date(2017, 1, 3), start_date - timedelta(days=14))
        while current_date <= end_date:
            indicative_observations.append(
                {
                    'd': current_date.isoformat(), 'FXUSDCAD': {
                        'v': rate
                    }
                }
            )
            current_date += timedelta(days=1)
        requests_mock.get(
            f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
            json={"observations": indicative_observations}
        )


def test_superficial_loss_with_prior_purchase(requests_mock):
    """Test superficial loss when purchase is before the loss (MSFT
    transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2022, 1, 1), date(2022, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2022',
            '-t',
            'MSFT',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'MSFT' in data
    msft_data = data['MSFT']

    assert msft_data['year'] == 2022
    assert msft_data['total_gains'] == 0
    # All transactions should be superficial losses
    assert len(msft_data['transactions']) == 0


def test_superficial_loss_with_subsequent_purchase(requests_mock):
    """Test superficial loss when purchase is after the loss (GOOGL
    transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2022, 1, 1), date(2022, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2022',
            '-t',
            'GOOGL',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'GOOGL' in data
    googl_data = data['GOOGL']

    assert googl_data['year'] == 2022
    assert googl_data['total_gains'] == 0
    # All transactions should be superficial losses
    assert len(googl_data['transactions']) == 0


def test_superficial_loss_edge_case(requests_mock):
    """Test superficial loss with purchase exactly on 30-day boundary (EDGE
    transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2024',
            '-t',
            'EDGE',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'EDGE' in data
    edge_data = data['EDGE']

    assert edge_data['year'] == 2024
    assert edge_data['total_gains'] == 0
    assert len(edge_data['transactions']) == 0  # Should be a superficial loss


def test_loss_just_outside_window(requests_mock):
    """Test loss with purchase just outside 30-day window (OUTSIDE
    transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2024',
            '-t',
            'OUTSIDE',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'OUTSIDE' in data
    outside_data = data['OUTSIDE']

    transactions = outside_data['transactions']
    # Should have one transaction (not superficial)
    assert len(transactions) == 1

    tx = transactions[0]
    assert tx['quantity'] == 50
    assert tx['capital_gain'] < 0  # Should be a regular loss


def test_multiple_purchases_in_window(requests_mock):
    """Test superficial loss with multiple purchases in window (MULTI
    transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2024',
            '-t',
            'MULTI',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'MULTI' in data
    multi_data = data['MULTI']

    assert multi_data['year'] == 2024
    assert multi_data['total_gains'] == 0
    assert len(multi_data['transactions']) == 0  # Should be a superficial loss


def test_zero_balance_at_window_end(requests_mock):
    """Test that a loss is not superficial if share balance is 0 at end of
    window (ZERO transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2024',
            '-t',
            'ZERO',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'ZERO' in data
    zero_data = data['ZERO']

    transactions = zero_data['transactions']
    assert len(transactions) == 2  # Should have both transactions

    # First transaction should be a regular loss (not superficial) since share
    # balance is 0 at end of window
    assert transactions[0]['capital_gain'] < 0

    # Second transaction should be a regular gain/loss
    assert transactions[1]['capital_gain'] != 0


def test_different_ticker_in_window(requests_mock):
    """Test that purchases of different tickers don't affect superficial loss
    (DIFF transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_superficial.csv'),
            '2024',
            '-t',
            'DIFF',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'DIFF' in data
    diff_data = data['DIFF']

    assert diff_data['year'] == 2024
    assert diff_data['total_gains'] == 0
    # Should be a superficial loss since there's a buy of DIFF within the
    # window
    assert len(diff_data['transactions']) == 0
