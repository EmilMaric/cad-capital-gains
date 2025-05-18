from datetime import date
from click.testing import CliRunner
import json

from capgains.cli import capgains
from tests.helpers import create_csv_file
from tests.test_comprehensive_basic import setup_exchange_rates_mock


def test_zero_commission_transactions(requests_mock, tmpdir):
    """Test transactions with zero commissions to ensure they're handled
    correctly."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2023, 1, 1), date(2023, 12, 31)
    )

    transactions = [
        # Buy 100 shares with no commission
        [
            "2023-01-15",
            "Zero Commission Buy",
            "ZERO",
            "BUY",
            "100",
            "50.00",
            "0.00",
            "USD"
        ],
        # Sell 50 shares with no commission
        [
            "2023-02-15",
            "Zero Commission Sell",
            "ZERO",
            "SELL",
            "50",
            "55.00",
            "0.00",
            "USD"
        ]
    ]

    csv_path = create_csv_file(
        tmpdir, "test_zero_commission.csv", transactions
    )
    runner = CliRunner()
    result = runner.invoke(
        capgains, ['calc', csv_path, '2023', '-t', 'ZERO', '--format', 'json']
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'ZERO' in data
    zero_data = data['ZERO']

    # Initial purchase: (100 × 50.00 + 0.00) × 2.0 = 10,000.00 CAD
    # ACB per share = 10,000.00 / 100 = 100.00 CAD

    # Sale:
    # Proceeds = (50 × 55.00) × 2.0 = 5,500.00 CAD
    # ACB = 50 × 100.00 = 5,000.00 CAD
    # Commission = 0.00 CAD
    # Capital gain = 5,500.00 - 5,000.00 - 0.00 = 500.00 CAD

    tx = zero_data['transactions'][0]
    assert abs(tx['proceeds'] - 5500.00) < 0.01
    assert abs(tx['acb'] - 5000.00) < 0.01
    assert abs(tx['outlays']) < 0.01  # Should be exactly 0
    assert abs(tx['capital_gain'] - 500.00) < 0.01


def test_small_commission_rounding(requests_mock, tmpdir):
    """Test transactions with very small commissions to verify rounding
    behavior."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2023, 1, 1), date(2023, 12, 31)
    )

    transactions = [
        # Buy with small commission
        [
            "2023-01-15",
            "Small Commission Buy",
            "SMALL",
            "BUY",
            "100",
            "50.00",
            "0.01",
            "USD"
        ],
        # Sell with small commission
        [
            "2023-02-15",
            "Small Commission Sell",
            "SMALL",
            "SELL",
            "50",
            "55.00",
            "0.005",
            "USD"
        ]
    ]

    csv_path = create_csv_file(
        tmpdir, "test_small_commission.csv", transactions
    )
    runner = CliRunner()
    result = runner.invoke(
        capgains,
        ['calc', csv_path, '2023', '-t', 'SMALL', '--format', 'json']
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'SMALL' in data
    small_data = data['SMALL']

    # Initial purchase: (100 × 50.00 + 0.01) × 2.0 = 10,000.02 CAD
    # ACB per share = 10,000.02 / 100 = 100.0002 CAD

    # Sale:
    # Proceeds = (50 × 55.00) × 2.0 = 5,500.00 CAD
    # ACB = 50 × 100.0002 = 5,000.01 CAD
    # Commission = 0.005 × 2.0 = 0.01 CAD
    # Capital gain = 5,500.00 - 5,000.01 - 0.01 = 499.98 CAD

    tx = small_data['transactions'][0]
    assert abs(tx['proceeds'] - 5500.00) < 0.01
    assert abs(tx['acb'] - 5000.01) < 0.01
    assert abs(tx['outlays'] - 0.01) < 0.01
    assert abs(tx['capital_gain'] - 499.98) < 0.01


def test_same_day_mixed_currency_commission(requests_mock, tmpdir):
    """Test commission handling for multiple currency transactions on the same
    day."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2023, 1, 1), date(2023, 12, 31)
    )

    transactions = [
        # Buy USD stock with USD commission
        [
            "2023-01-15",
            "USD Buy",
            "MIXED",
            "BUY",
            "100",
            "50.00",
            "9.99",
            "USD"
        ],
        # Buy CAD stock with CAD commission
        [
            "2023-01-15",
            "CAD Buy",
            "XIU.TO",
            "BUY",
            "200",
            "25.00",
            "9.99",
            "CAD"
        ],
        # Sell USD stock with USD commission
        [
            "2023-02-15",
            "USD Sell",
            "MIXED",
            "SELL",
            "50",
            "55.00",
            "9.99",
            "USD"
        ],
        # Sell CAD stock with CAD commission
        [
            "2023-02-15",
            "CAD Sell",
            "XIU.TO",
            "SELL",
            "100",
            "27.00",
            "9.99",
            "CAD"
        ]
    ]

    csv_path = create_csv_file(tmpdir, "test_mixed_currency.csv", transactions)
    runner = CliRunner()
    result = runner.invoke(
        capgains, ['calc', csv_path, '2023', '--format', 'json']
    )
    assert result.exit_code == 0

    data = json.loads(result.output)

    # USD Stock (MIXED):
    # Initial purchase: (100 × 50.00 + 9.99) × 2.0 = 10,019.98 CAD
    # ACB per share = 10,019.98 / 100 = 100.1998 CAD

    # Sale:
    # Proceeds = (50 × 55.00) × 2.0 = 5,500.00 CAD
    # ACB = 50 × 100.1998 = 5,009.99 CAD
    # Commission = 9.99 × 2.0 = 19.98 CAD
    # Capital gain = 5,500.00 - 5,009.99 - 19.98 = 470.03 CAD

    mixed_tx = next(
        tx for tx in data['MIXED']['transactions']
        if tx['description'] == 'USD Sell'
    )
    assert abs(mixed_tx['proceeds'] - 5500.00) < 0.01
    assert abs(mixed_tx['acb'] - 5009.99) < 0.01
    assert abs(mixed_tx['outlays'] - 19.98) < 0.01
    assert abs(mixed_tx['capital_gain'] - 470.03) < 0.01

    # CAD Stock (XIU.TO):
    # Initial purchase: (200 × 25.00 + 9.99) = 5,009.99 CAD
    # ACB per share = 5,009.99 / 200 = 25.04995 CAD

    # Sale:
    # Proceeds = 100 × 27.00 = 2,700.00 CAD
    # ACB = 100 × 25.04995 = 2,504.995 CAD
    # Commission = 9.99 CAD
    # Capital gain = 2,700.00 - 2,504.995 - 9.99 = 185.015 CAD

    xiu_tx = next(
        tx for tx in data['XIU.TO']['transactions']
        if 'CAD Sell' in tx['description']
    )
    assert abs(xiu_tx['proceeds'] - 2700.00) < 0.01
    assert abs(xiu_tx['acb'] - 2504.995) < 0.01
    assert abs(xiu_tx['outlays'] - 9.99) < 0.01
    assert abs(xiu_tx['capital_gain'] - 185.015) < 0.01


def test_commission_in_superficial_loss(requests_mock, tmpdir):
    """Test commission handling in superficial loss scenarios."""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(
        requests_mock, date(2023, 1, 1), date(2023, 12, 31)
    )

    transactions = [
        # Initial buy
        [
            "2023-01-15",
            "Initial Buy",
            "SUPER",
            "BUY",
            "100",
            "50.00",
            "9.99",
            "USD"
        ],
        # Sell at a loss
        [
            "2023-02-15",
            "Loss Sale",
            "SUPER",
            "SELL",
            "50",
            "40.00",
            "9.99",
            "USD"
        ],
        # Buy back within 30 days (triggering superficial loss)
        [
            "2023-03-01",
            "Buy Back",
            "SUPER",
            "BUY",
            "50",
            "45.00",
            "9.99",
            "USD"
        ]
    ]

    csv_path = create_csv_file(
        tmpdir, "test_superficial_loss.csv", transactions
    )
    runner = CliRunner()
    result = runner.invoke(
        capgains,
        ['calc', csv_path, '2023', '-t', 'SUPER', '--format', 'json']
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert 'SUPER' in data
    super_data = data['SUPER']

    # Initial purchase: (100 × 50.00 + 9.99) × 2.0 = 10,019.98 CAD
    # ACB per share = 10,019.98 / 100 = 100.1998 CAD

    # Loss sale:
    # Proceeds = (50 × 40.00) × 2.0 = 4,000.00 CAD
    # ACB = 50 × 100.1998 = 5,009.99 CAD
    # Commission = 9.99 × 2.0 = 19.98 CAD
    # Capital loss = 4,000.00 - 5,009.99 - 19.98 = -1,029.97 CAD
    # This loss should be denied due to superficial loss rules

    # Buy back:
    # Cost = (50 × 45.00 + 9.99) × 2.0 = 4,519.98 CAD
    # Denied loss is added to ACB of new shares

    # The transaction should not appear in the output since it's a superficial
    # loss
    assert len(super_data['transactions']) == 0
    # Total gains should be 0 since the loss was denied
    assert abs(super_data['total_gains']) < 0.01
