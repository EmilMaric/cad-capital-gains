import os
import json
from click.testing import CliRunner
from datetime import date
from decimal import Decimal

from capgains.cli import capgains
from capgains.transaction import Transaction
from capgains.transactions import Transactions


def test_show_json_output():
    """Test JSON output for show command"""
    # Create test transactions
    transactions = [
        Transaction(
            date(2022, 1, 15),
            'Buy AAPL',
            'AAPL',
            'BUY',
            100,
            150.00,
            9.99,
            'USD'
        ),
        Transaction(
            date(2022, 2, 15),
            'Sell AAPL',
            'AAPL',
            'SELL',
            50,
            180.00,
            9.99,
            'USD'
        )
    ]

    # Run command with JSON output
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write test data to CSV
        with open('test.csv', 'w') as f:
            f.write('2022-01-15,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD\n')
            f.write('2022-02-15,Sell AAPL,AAPL,SELL,50,180.00,9.99,USD\n')

        # Test without exchange rates
        result = runner.invoke(capgains, ['show', 'test.csv', '--format', 'json'])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert 'transactions' in data
        assert len(data['transactions']) == 2

        # Test with exchange rates
        result = runner.invoke(capgains, ['show', 'test.csv', '-e', '--format', 'json'])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert 'transactions' in data
        assert len(data['transactions']) == 2
        assert 'exchange_rate' in data['transactions'][0]


def test_calc_json_output():
    """Test JSON output for calc command"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write test data to CSV
        with open('test.csv', 'w') as f:
            f.write('2022-01-15,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD\n')
            f.write('2022-02-15,Sell AAPL,AAPL,SELL,50,180.00,9.99,USD\n')

        result = runner.invoke(capgains, ['calc', 'test.csv', '2022', '--format', 'json'])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert 'AAPL' in data
        aapl_data = data['AAPL']
        assert aapl_data['year'] == 2022
        assert 'total_gains' in aapl_data
        assert 'transactions' in aapl_data


def test_maxcost_json_output():
    """Test JSON output for maxcost command"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write test data to CSV
        with open('test.csv', 'w') as f:
            f.write('2022-01-15,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD\n')
            f.write('2022-02-15,Buy More AAPL,AAPL,BUY,50,180.00,9.99,USD\n')

        result = runner.invoke(capgains, ['maxcost', 'test.csv', '2022', '--format', 'json'])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert 'AAPL' in data
        aapl_data = data['AAPL']
        assert aapl_data['year'] == 2022
        assert 'max_cost' in aapl_data
        assert 'year_end_cost' in aapl_data


def test_json_output_no_results():
    """Test JSON output when no results are found"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write test data to CSV
        with open('test.csv', 'w') as f:
            f.write('2022-01-15,Buy AAPL,AAPL,BUY,100,150.00,9.99,USD\n')

        # Test show command
        result = runner.invoke(capgains, ['show', 'test.csv', '-t', 'MSFT', '--format', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'error' in data

        # Test calc command
        result = runner.invoke(capgains, ['calc', 'test.csv', '2022', '-t', 'MSFT', '--format', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'error' in data

        # Test maxcost command
        result = runner.invoke(capgains, ['maxcost', 'test.csv', '2022', '-t', 'MSFT', '--format', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'error' in data 