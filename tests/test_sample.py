import os
import pytest
from click.testing import CliRunner
from capgains.cli import capgains
from capgains.transactions_reader import TransactionsReader


def test_sample_csv_exists():
    """Verify that the sample CSV file exists in the tests directory"""
    assert os.path.exists(os.path.join('tests', 'sample.csv'))


def test_can_read_sample_csv():
    """Verify that we can read and parse the sample CSV file"""
    transactions = TransactionsReader.get_transactions(os.path.join('tests', 'sample.csv'))
    assert len(transactions) == 36  # Updated number of transactions in sample.csv
    
    # Verify we have the expected tickers
    expected_tickers = {'AAPL', 'GOOGL', 'TD.TO', 'RY.TO', 'VFV.TO', 'MSFT', 'SHOP.TO'}
    assert set(transactions.tickers) == expected_tickers

    # Verify we have both currencies
    currencies = {t.currency for t in transactions}
    assert currencies == {'USD', 'CAD'}

    # Verify we have transactions across all years
    years = {t.date.year for t in transactions}
    assert years == {2022, 2023, 2024}


def test_maxcost_sample_2022():
    """Test the maxcost command with sample.csv for 2022"""
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', os.path.join('tests', 'sample.csv'), '2022'])
    assert result.exit_code == 0
    assert 'AAPL-2022' in result.output
    assert 'GOOGL-2022' in result.output
    assert 'TD.TO-2022' in result.output
    assert 'VFV.TO-2022' in result.output
    # Verify some costs are shown
    assert 'Max cost =' in result.output
    assert 'Year end =' in result.output


def test_maxcost_sample_2023():
    """Test the maxcost command with sample.csv for 2023"""
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', os.path.join('tests', 'sample.csv'), '2023'])
    assert result.exit_code == 0
    assert 'AAPL-2023' in result.output
    assert 'GOOGL-2023' in result.output
    assert 'TD.TO-2023' in result.output
    assert 'RY.TO-2023' in result.output
    assert 'VFV.TO-2023' in result.output


def test_maxcost_sample_2024():
    """Test the maxcost command with sample.csv for 2024"""
    runner = CliRunner()
    result = runner.invoke(capgains, ['maxcost', os.path.join('tests', 'sample.csv'), '2024'])
    assert result.exit_code == 0
    assert 'AAPL-2024' in result.output
    assert 'MSFT-2024' in result.output
    assert 'SHOP.TO-2024' in result.output
    assert 'VFV.TO-2024' in result.output


def test_calc_sample_2022():
    """Test the calc command with sample.csv for 2022"""
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'sample.csv'), '2022'])
    assert result.exit_code == 0
    # Verify we see capital gains output for stocks we sold in 2022
    assert 'AAPL-2022' in result.output
    assert 'GOOGL-2022' in result.output
    assert 'TD.TO-2022' in result.output
    assert 'VFV.TO-2022' in result.output
    assert 'Total Gains' in result.output


def test_calc_sample_2023():
    """Test the calc command with sample.csv for 2023"""
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'sample.csv'), '2023'])
    assert result.exit_code == 0
    # Verify we see capital gains output for stocks we sold in 2023
    assert 'AAPL-2023' in result.output
    assert 'GOOGL-2023' in result.output
    assert 'TD.TO-2023' in result.output
    assert 'RY.TO-2023' in result.output
    assert 'VFV.TO-2023' in result.output
    assert 'Total Gains' in result.output


def test_calc_sample_2024():
    """Test the calc command with sample.csv for 2024"""
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'sample.csv'), '2024'])
    assert result.exit_code == 0
    # Verify we see capital gains output for stocks we sold in 2024
    assert 'AAPL-2024' in result.output
    assert 'MSFT-2024' in result.output
    assert 'SHOP.TO-2024' in result.output
    assert 'VFV.TO-2024' in result.output
    assert 'Total Gains' in result.output


def test_show_sample():
    """Test the show command with sample.csv"""
    runner = CliRunner()
    # Test showing all transactions
    result = runner.invoke(capgains, ['show', os.path.join('tests', 'sample.csv')])
    assert result.exit_code == 0
    assert '2022' in result.output
    assert '2023' in result.output
    assert '2024' in result.output
    
    # Test filtering by ticker
    result = runner.invoke(capgains, ['show', os.path.join('tests', 'sample.csv'), '-t', 'AAPL'])
    assert result.exit_code == 0
    assert 'AAPL' in result.output
    assert 'GOOGL' not in result.output
    
    # Test showing exchange rates
    result = runner.invoke(capgains, ['show', os.path.join('tests', 'sample.csv'), '-e'])
    assert result.exit_code == 0
    assert 'exchange' in result.output 