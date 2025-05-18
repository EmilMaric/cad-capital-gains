import os
import json
from datetime import date
from click.testing import CliRunner
from capgains.cli import capgains
from tests.test_comprehensive_superficial import setup_exchange_rates_mock


def test_overlapping_loss_windows(requests_mock):
    """Test realistic overlapping superficial loss windows where trades happen
    naturally close together."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_edge_cases.csv'),
            '2024',
            '-t',
            'OVERLAP',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'OVERLAP' in data
    overlap_data = data['OVERLAP']

    # Initial Buy: 100 × $100.00 × 2.0 = $20,000.00 CAD
    # Commission: $9.99 × 2.0 = $19.98 CAD
    # Total ACB = $20,000.00 + $19.98 = $20,019.98 CAD
    # ACB per share = $20,019.98 / 100 = $200.20 CAD

    # First Loss: 30 × $90.00 × 2.0 = $5,400.00 CAD proceeds
    # Commission: $9.99 × 2.0 = $19.98 CAD
    # ACB portion = 30 × $200.20 = $6,006.00 CAD
    # Capital loss = $5,400.00 - $19.98 - $6,006.00 = -$625.98 CAD
    # (superficial)

    transactions = overlap_data['transactions']
    assert len(transactions) == 0  # Both losses should be superficial

    # First loss window: Jan 15 ± 30 days (Dec 16 - Feb 14)
    # Second loss window: Jan 30 ± 30 days (Dec 31 - Mar 1)
    # Buy on Feb 10 falls within both windows and we still own shares after
    # both windows


def test_invalid_transaction_protection(requests_mock):
    """Test that the code protects against invalid transactions that would
    create negative balances."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_edge_cases.csv'),
            '2024',
            '-t',
            'PROTECT',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 1  # Should fail due to invalid transaction
    assert "Transaction caused negative share balance" in result.output


def test_natural_zero_balance(requests_mock):
    """Test a realistic sequence of trades that happens to end at zero
    balance."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_edge_cases.csv'),
            '2024',
            '-t',
            'EXACT',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'EXACT' in data
    exact_data = data['EXACT']

    # Initial Buy: 100 × $75.00 × 2.0 = $15,000.00 CAD
    # Commission: $9.99 × 2.0 = $19.98 CAD
    # Total ACB = $15,000.00 + $19.98 = $15,019.98 CAD
    # ACB per share = $15,019.98 / 100 = $150.20 CAD

    # Small Sell 1: 30 × $70.00 × 2.0 = $4,200.00 CAD proceeds
    # Commission: $9.99 × 2.0 = $19.98 CAD
    # ACB portion = 30 × $150.20 = $4,506.00 CAD
    # Capital loss = $4,200.00 - $19.98 - $4,506.00 = -$325.98 CAD

    transactions = exact_data['transactions']
    assert len(transactions) == 3  # Should have all three sell transactions

    # Verify first sell transaction
    first_sell = next(
        tx for tx in transactions if tx['description'] == 'Small Sell 1'
    )
    assert abs(first_sell['proceeds'] - 4200.00) < 0.01  # 30 × $70.00 × 2.0
    assert abs(first_sell['outlays'] - 19.98) < 0.01  # $9.99 × 2.0
    assert abs(first_sell['acb'] - 4506.00) < 0.01  # 30 × $150.20
    # $4,200.00 - $19.98 - $4,506.00
    assert abs(first_sell['capital_gain'] + 325.98) < 0.01

    # All losses should be regular since we end with zero balance
    sell_transactions = [
        tx for tx in transactions
        if tx['description'].startswith('Small Sell')
        or tx['description'] == 'Final Sell'
    ]
    assert len(sell_transactions) == 3
    for tx in sell_transactions:
        # Should be regular losses, not superficial
        assert tx['capital_gain'] < 0


def test_window_boundary_trades(requests_mock):
    """Test realistic trading around superficial loss window boundaries."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2024, 1, 1), date(2024, 12, 31)
    )

    runner = CliRunner()
    result = runner.invoke(
        capgains,
        [
            'calc',
            os.path.join('tests', 'comprehensive_edge_cases.csv'),
            '2024',
            '-t',
            'WINDOW',
            '--format',
            'json'
        ]
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'WINDOW' in data
    window_data = data['WINDOW']

    # Initial Buy: 100 × $200.00 × 2.0 = $40,000.00 CAD
    # Commission: $9.99 × 2.0 = $19.98 CAD
    # Total ACB = $40,000.00 + $19.98 = $40,019.98 CAD
    # ACB per share = $40,019.98 / 100 = $400.20 CAD

    # First Loss: 40 × $180.00 × 2.0 = $14,400.00 CAD proceeds
    # Commission: $9.99 × 2.0 = $19.98 CAD
    # ACB portion = 40 × $400.20 = $16,008.00 CAD
    # Capital loss = $14,400.00 - $19.98 - $16,008.00 = -$1,627.98 CAD
    # (superficial)

    transactions = window_data['transactions']
    assert len(transactions) == 0  # Both should be superficial losses
