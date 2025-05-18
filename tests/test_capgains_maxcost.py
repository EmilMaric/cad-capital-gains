from datetime import date, timedelta
import pytest
from click.testing import CliRunner
import tempfile
import csv
import os
import requests_mock as rm

from capgains.cli import capgains
from capgains.commands.capgains_maxcost import _get_max_cost, _get_year_end_cost, calculate_costs
from capgains.transaction import Transaction
from capgains.transactions import Transactions
from capgains.exchange_rate import ExchangeRate


def create_csv_file(transactions):
    """Helper function to create a temporary CSV file with transactions"""
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w', newline='') as f:
        writer = csv.writer(f)
        for t in transactions:
            writer.writerow([
                t.date.strftime('%Y-%m-%d'),
                t.description,
                t.ticker,
                t.action,
                t.qty,
                t.price,
                t.commission,
                t.currency
            ])
    return path


def setup_exchange_rates_mock(requests_mock, transactions):
    """Helper function to set up exchange rate mocking for a list of transactions"""
    # Get the earliest and latest dates
    dates = [t.date for t in transactions]
    if not dates:
        return
    
    # For noon rates (before 2017-01-03)
    noon_observations = []
    min_date = min(dates)
    if min_date < date(2017, 1, 3):
        # Add noon rates from min_date to 2017-01-02
        current_date = min_date - timedelta(days=14)  # Account for double 7-day lookback
        end_date = min(max(dates), date(2017, 1, 2))
        while current_date <= end_date:
            noon_observations.append({
                'd': current_date.isoformat(),
                'IEXE0101': {
                    'v': '2.0'
                }
            })
            current_date += timedelta(days=1)
        requests_mock.get(
            f"{ExchangeRate.valet_obs_url}/IEXE0101/json",
            json={"observations": noon_observations}
        )
    
    # For indicative rates (after 2017-01-03)
    indicative_observations = []
    if max(dates) >= date(2017, 1, 3):
        # Add indicative rates from 2017-01-03 to max_date
        current_date = max(date(2017, 1, 3), min_date - timedelta(days=14))
        while current_date <= max(dates):
            indicative_observations.append({
                'd': current_date.isoformat(),
                'FXUSDCAD': {
                    'v': '2.0'
                }
            })
            current_date += timedelta(days=1)
        requests_mock.get(
            f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
            json={"observations": indicative_observations}
        )


def test_basic_max_cost(requests_mock):
    """Test basic max cost calculation within a single year"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'Buy',
            'AAPL',
            'BUY',
            100,
            150.00,  # Total cost: 15,000 USD = 30,000 CAD
            0.00,
            'USD'
        ),
        Transaction(
            date(2018, 6, 1),
            'Buy More',
            'AAPL',
            'BUY',
            50,
            200.00,  # Additional 10,000 USD = 20,000 CAD, Total: 50,000 CAD
            0.00,
            'USD'
        ),
        Transaction(
            date(2018, 12, 1),
            'Sell Half',
            'AAPL',
            'SELL',
            75,
            180.00,  # Reduces by 25,000 CAD (75 shares * 333.33 ACB/share), End: 25,000 CAD
            0.00,
            'USD'
        )
    ]
    setup_exchange_rates_mock(requests_mock, transactions)
    csv_path = create_csv_file(transactions)
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', csv_path, '2018'])
    
    os.unlink(csv_path)
    
    assert result.exit_code == 0
    assert "Max cost = 50,000.00" in result.output
    assert "Year end = 25,000.00" in result.output  # Updated to match actual ACB calculation


def test_multi_year_max_cost(requests_mock):
    """Test max cost calculation across multiple years with previous year consideration"""
    transactions = [
        Transaction(
            date(2017, 6, 1),
            'Initial Buy',
            'GOOGL',
            'BUY',
            100,
            100.00,  # 10,000 USD = 20,000 CAD
            0.00,
            'USD'
        ),
        Transaction(
            date(2018, 1, 1),
            'Buy More',
            'GOOGL',
            'BUY',
            50,
            150.00,  # Additional 7,500 USD = 15,000 CAD, Total: 35,000 CAD
            0.00,
            'USD'
        ),
        Transaction(
            date(2018, 12, 31),
            'Sell Some',
            'GOOGL',
            'SELL',
            75,
            200.00,  # Reduces by 26,250 CAD, End: 8,750 CAD
            0.00,
            'USD'
        )
    ]
    setup_exchange_rates_mock(requests_mock, transactions)
    transactions = Transactions(transactions)
    
    # Calculate costs first
    transactions_with_costs = calculate_costs(transactions, 2018, 'GOOGL')
    
    # Test 2017
    result = _get_max_cost(transactions_with_costs, 2017, 2017)
    assert result == 20000.00
    
    # Test 2018 (should consider 2017 year-end)
    result = _get_max_cost(transactions_with_costs, 2018, 2017)
    assert result == 35000.00


def test_multi_currency_max_cost(requests_mock):
    """Test max cost calculation with mixed CAD and USD transactions"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'Buy CAD',
            'TD',
            'BUY',
            100,
            50.00,  # 5,000 CAD
            0.00,
            'CAD'
        ),
        Transaction(
            date(2018, 6, 1),
            'Buy USD',
            'TD',
            'BUY',
            100,
            75.00,  # 7,500 USD = 15,000 CAD, Total: 20,000 CAD
            0.00,
            'USD'
        )
    ]
    setup_exchange_rates_mock(requests_mock, transactions)
    csv_path = create_csv_file(transactions)
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', csv_path, '2018'])
    
    os.unlink(csv_path)
    
    assert result.exit_code == 0
    assert "Max cost = 20,000.00" in result.output
    assert "Year end = 20,000.00" in result.output


def test_year_end_cost_fallback(requests_mock):
    """Test year-end cost calculation with fallback to previous years"""
    transactions = [
        Transaction(
            date(2017, 1, 1),
            'Buy',
            'MSFT',
            'BUY',
            100,
            50.00,  # 5,000 USD = 10,000 CAD
            0.00,
            'USD'
        ),
        # No transactions in 2018
        Transaction(
            date(2019, 1, 1),
            'Buy More',
            'MSFT',
            'BUY',
            50,
            100.00,  # Additional 5,000 USD = 10,000 CAD, Total: 20,000 CAD
            0.00,
            'USD'
        )
    ]
    setup_exchange_rates_mock(requests_mock, transactions)
    transactions = Transactions(transactions)
    
    # Calculate costs first
    transactions_with_costs = calculate_costs(transactions, 2019, 'MSFT')
    
    # 2018 should fall back to 2017 year-end cost
    result = _get_year_end_cost(transactions_with_costs, 2018, 2017)
    assert result == 10000.00


def test_t1135_threshold_warning(requests_mock):
    """Test max cost calculation near the T1135 reporting threshold ($100,000 CAD)"""
    transactions = [
        Transaction(
            date(2018, 1, 1),
            'Large Buy',
            'SPY',
            'BUY',
            1000,
            90.00,  # 90,000 USD = 180,000 CAD
            0.00,
            'USD'
        ),
        Transaction(
            date(2018, 6, 1),
            'Sell Most',
            'SPY',
            'SELL',
            900,
            95.00,  # Reduces by 162,000 CAD, End: 18,000 CAD
            0.00,
            'USD'
        )
    ]
    setup_exchange_rates_mock(requests_mock, transactions)
    csv_path = create_csv_file(transactions)
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', csv_path, '2018'])
    
    os.unlink(csv_path)
    
    assert result.exit_code == 0
    assert "Max cost = 180,000.00" in result.output  # Above T1135 threshold
    assert "Year end = 18,000.00" in result.output   # Below T1135 threshold


def test_empty_transactions():
    """Test handling of empty transaction list"""
    csv_path = create_csv_file([])
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', csv_path, '2018'])
    
    os.unlink(csv_path)
    
    assert result.exit_code == 0
    assert "No transactions available" in result.output


def test_year_min_boundary(requests_mock):
    """Test handling of year_min boundary in cost calculations"""
    transactions = [
        Transaction(
            date(2017, 1, 1),
            'Buy',
            'NVDA',
            'BUY',
            100,
            50.00,  # 5,000 USD = 10,000 CAD
            0.00,
            'USD'
        )
    ]
    setup_exchange_rates_mock(requests_mock, transactions)
    transactions = Transactions(transactions)
    
    # Calculate costs first
    transactions_with_costs = calculate_costs(transactions, 2017, 'NVDA')
    
    # Testing at year_min boundary
    result = _get_year_end_cost(transactions_with_costs, 2017, 2017)
    assert result == 10000.00
    
    # Testing before year_min (should return 0)
    result = _get_year_end_cost(transactions_with_costs, 2016, 2017)
    assert result == 0 