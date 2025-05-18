import os
import json
from datetime import date, timedelta
from click.testing import CliRunner
from capgains.cli import capgains
from capgains.exchange_rate import ExchangeRate
from tests.helpers import create_csv_file, create_json_file, transactions_to_list

def setup_exchange_rates_mock(requests_mock, start_date, end_date, rate='2.0'):
    """Helper function to set up exchange rate mocking for a date range"""
    # For noon rates (before 2017-01-03)
    noon_observations = []
    if start_date < date(2017, 1, 3):
        # Add noon rates from start_date to 2017-01-02
        current_date = start_date - timedelta(days=14)  # Account for double 7-day lookback
        end_noon = min(end_date, date(2017, 1, 2))
        while current_date <= end_noon:
            noon_observations.append({
                'd': current_date.isoformat(),
                'IEXE0101': {
                    'v': rate
                }
            })
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
            indicative_observations.append({
                'd': current_date.isoformat(),
                'FXUSDCAD': {
                    'v': rate
                }
            })
            current_date += timedelta(days=1)
        requests_mock.get(
            f"{ExchangeRate.valet_obs_url}/FXUSDCAD/json",
            json={"observations": indicative_observations}
        )

def clean_number(num_str):
    """Convert a number string with commas to float"""
    return float(num_str.replace(',', ''))

def test_regular_gains_and_losses(requests_mock):
    """Test regular capital gains and losses (AAPL transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(requests_mock, date(2022, 1, 1), date(2022, 12, 31))
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'comprehensive_basic.csv'), '2022', '-t', 'AAPL', '--format', 'json'])
    assert result.exit_code == 0
    
    data = json.loads(result.output)
    assert 'AAPL' in data
    aapl_data = data['AAPL']
    
    assert aapl_data['year'] == 2022
    assert abs(aapl_data['total_gains'] - 9320.055) < 0.01  # Total gains = 8,720.03 + 600.025 = 9,320.055 CAD
    
    transactions = aapl_data['transactions']
    assert len(transactions) == 2  # Should have two transactions
    
    # Find gain and loss transactions
    gain_tx = next(tx for tx in transactions if 'Regular Gain AAPL' in tx['description'])
    loss_tx = next(tx for tx in transactions if 'Regular Loss AAPL' in tx['description'])
    
    # Initial purchase: (100 × 142.50 + 9.99) × 2.0 = 28,519.98 CAD
    # ACB per share = 28,519.98 / 100 = 285.1998 CAD
    
    # First sale (50 shares):
    # Proceeds = (50 × 230.00) × 2.0 = 23,000.00 CAD
    # ACB = 50 × 285.1998 = 14,259.99 CAD
    # Commission = 9.99 × 2.0 = 19.98 CAD
    # Capital gain = 23,000.00 - 14,259.99 - 19.98 = 8,720.03 CAD
    
    # Second sale (25 shares):
    # Proceeds = (25 × 155.00) × 2.0 = 7,750.00 CAD
    # ACB = 25 × 285.1998 = 7,129.995 CAD
    # Commission = 9.99 × 2.0 = 19.98 CAD
    # Capital gain = 7,750.00 - 7,129.995 - 19.98 = 600.025 CAD
    
    # Total gains = 8,720.03 + 600.025 = 9,320.055 CAD
    
    # Verify gain transaction
    assert gain_tx['quantity'] == 50
    assert abs(gain_tx['proceeds'] - 23000.00) < 0.01  # (50 × 230.00) × 2.0
    assert abs(gain_tx['acb'] - 14259.99) < 0.01  # 50 × (28519.98/100)
    assert abs(gain_tx['outlays'] - 19.98) < 0.01  # 9.99 × 2.0
    assert abs(gain_tx['capital_gain'] - 8720.03) < 0.01  # 23000.00 - 14259.99 - 19.98
    
    # Verify loss transaction
    assert loss_tx['quantity'] == 25
    assert abs(loss_tx['proceeds'] - 7750.00) < 0.01  # (25 × 155.00) × 2.0
    assert abs(loss_tx['acb'] - 7129.995) < 0.01  # 25 × (28519.98/100)
    assert abs(loss_tx['outlays'] - 19.98) < 0.01  # 9.99 × 2.0
    assert abs(loss_tx['capital_gain'] - 600.025) < 0.01  # 7750.00 - 7129.995 - 19.98

def test_partial_share_transactions(requests_mock):
    """Test gains/losses with partial share quantities (VFV.TO transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(requests_mock, date(2022, 1, 1), date(2022, 12, 31))
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'comprehensive_basic.csv'), '2022', '-t', 'VFV.TO', '--format', 'json'])
    assert result.exit_code == 0
    
    data = json.loads(result.output)
    assert 'VFV.TO' in data
    vfv_data = data['VFV.TO']
    
    assert vfv_data['year'] == 2022
    
    transactions = vfv_data['transactions']
    assert len(transactions) == 1  # Should have one transaction
    
    # Verify partial share transaction
    tx = transactions[0]
    assert tx['quantity'] == 5.25
    
    # Initial purchase: (10.5 × 98.50 + 9.99) = 1044.24 CAD
    # ACB per share = 1044.24 / 10.5 = 99.45143... CAD
    # Sale proceeds = (5.25 × 99.50) = 522.375 CAD
    # ACB for sold shares = 5.25 × 99.45143... = 522.12 CAD
    # Commission = 9.99 CAD
    # Capital gain = 522.375 - 522.12 - 9.99 = -9.735 CAD
    
    assert abs(tx['proceeds'] - 522.375) < 0.01  # 5.25 × 99.50
    assert abs(tx['acb'] - 522.12) < 0.01  # 5.25 × (1044.24/10.5)
    assert abs(tx['outlays'] - 9.99) < 0.01  # Commission in CAD
    assert abs(tx['capital_gain'] + 9.735) < 0.01  # 522.375 - 522.12 - 9.99
    
    assert abs(vfv_data['total_gains'] + 9.735) < 0.01  # Same as transaction capital gain

def test_complete_sale_loss(requests_mock):
    """Test loss that's not superficial due to complete sale (TD.TO transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(requests_mock, date(2022, 1, 1), date(2022, 12, 31))
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'comprehensive_basic.csv'), '2022', '-t', 'TD.TO', '--format', 'json'])
    assert result.exit_code == 0
    
    data = json.loads(result.output)
    assert 'TD.TO' in data
    td_data = data['TD.TO']
    
    assert td_data['year'] == 2022
    
    transactions = td_data['transactions']
    assert len(transactions) == 1  # Should have one transaction
    
    # Initial purchase: (250 × 85.00 + 9.99) = 21,259.99 CAD
    # Sale proceeds = (250 × 79.00) = 19,750.00 CAD
    # Commission = 9.99 CAD
    # Capital loss = 19,750.00 - 21,259.99 - 9.99 = -1,519.98 CAD
    
    # Verify complete sale loss
    tx = transactions[0]
    assert tx['quantity'] == 250
    assert abs(tx['proceeds'] - 19750.00) < 0.01  # 250 × 79.00
    assert abs(tx['acb'] - 21259.99) < 0.01  # 250 × 85.00 + 9.99
    assert abs(tx['outlays'] - 9.99) < 0.01  # Commission in CAD
    assert abs(tx['capital_gain'] + 1519.98) < 0.01  # 19750.00 - 21259.99 - 9.99
    
    assert abs(td_data['total_gains'] + 1519.98) < 0.01  # Same as transaction capital loss

def test_mixed_currency_transactions(requests_mock):
    """Test gains/losses with mixed currency transactions (META transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(requests_mock, date(2023, 1, 1), date(2023, 12, 31))
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'comprehensive_basic.csv'), '2023', '-t', 'META', '--format', 'json'])
    assert result.exit_code == 0
    
    data = json.loads(result.output)
    assert 'META' in data
    meta_data = data['META']
    
    assert meta_data['year'] == 2023
    
    transactions = meta_data['transactions']
    assert len(transactions) == 2  # Should have two transactions
    
    # Initial purchase: (100 × 200.00 + 9.99) × 2.0 = 40,019.98 CAD
    # ACB per share = 40,019.98 / 100 = 400.1998 CAD
    
    # Find gain and loss transactions
    gain_tx = next(tx for tx in transactions if 'Quick Gain Meta' in tx['description'])
    loss_tx = next(tx for tx in transactions if 'Loss with Mixed Currency' in tx['description'])
    
    # First sale (USD):
    # Proceeds = (50 × 242.00) × 2.0 = 24,200.00 CAD
    # ACB = 50 × 400.1998 = 20,009.99 CAD
    # Commission = 9.99 × 2.0 = 19.98 CAD
    # Capital gain = 24,200.00 - 20,009.99 - 19.98 = 4,170.03 CAD
    
    # Verify gain transaction
    assert gain_tx['quantity'] == 50
    assert abs(gain_tx['proceeds'] - 24200.00) < 0.01  # (50 × 242.00) × 2.0
    assert abs(gain_tx['acb'] - 20009.99) < 0.01  # 50 × (40019.98/100)
    assert abs(gain_tx['outlays'] - 19.98) < 0.01  # 9.99 × 2.0
    assert abs(gain_tx['capital_gain'] - 4170.03) < 0.01  # 24200.00 - 20009.99 - 19.98
    
    # Second sale (CAD):
    # Proceeds = 25 × 190.00 = 4,750.00 CAD
    # ACB = 25 × 400.1998 = 10,004.995 CAD
    # Commission = 9.99 CAD
    # Capital loss = 4,750.00 - 10,004.995 - 9.99 = -5,264.985 CAD
    
    # Verify loss transaction
    assert loss_tx['quantity'] == 25
    assert abs(loss_tx['proceeds'] - 4750.00) < 0.01  # 25 × 190.00
    assert abs(loss_tx['acb'] - 10004.995) < 0.01  # 25 × (40019.98/100)
    assert abs(loss_tx['outlays'] - 9.99) < 0.01  # Commission in CAD
    assert abs(loss_tx['capital_gain'] + 5264.985) < 0.01  # 4750.00 - 10004.995 - 9.99
    
    # Total gains = 4170.03 - 5264.985 = -1094.955 CAD
    assert abs(meta_data['total_gains'] + 1094.955) < 0.01

def test_regular_cad_transactions(requests_mock):
    """Test regular gains/losses with CAD transactions (XIU.TO transactions)"""
    # Set up exchange rate mock for the date range
    setup_exchange_rates_mock(requests_mock, date(2023, 1, 1), date(2023, 12, 31))
    
    runner = CliRunner()
    result = runner.invoke(capgains, ['calc', os.path.join('tests', 'comprehensive_basic.csv'), '2023', '-t', 'XIU.TO', '--format', 'json'])
    assert result.exit_code == 0
    
    data = json.loads(result.output)
    assert 'XIU.TO' in data
    xiu_data = data['XIU.TO']
    
    assert xiu_data['year'] == 2023
    transactions = xiu_data['transactions']
    assert len(transactions) == 1  # Should have one transaction
    
    # Initial purchase: (500 × 25.50 + 9.99) = 12,759.99 CAD
    # ACB per share = 12,759.99 / 500 = 25.51998 CAD
    
    # Sale:
    # Proceeds = 200 × 27.50 = 5,500.00 CAD
    # ACB = 200 × 25.51998 = 5,103.996 CAD
    # Commission = 9.99 CAD
    # Capital gain = 5,500.00 - 5,103.996 - 9.99 = 386.014 CAD
    
    # Verify CAD gain transaction
    tx = transactions[0]
    assert tx['quantity'] == 200
    assert abs(tx['proceeds'] - 5500.00) < 0.01  # 200 × 27.50
    assert abs(tx['acb'] - 5103.996) < 0.01  # 200 × (12759.99/500)
    assert abs(tx['outlays'] - 9.99) < 0.01  # Commission in CAD
    assert abs(tx['capital_gain'] - 386.014) < 0.01  # 5500.00 - 5103.996 - 9.99
    
    assert abs(xiu_data['total_gains'] - 386.014) < 0.01  # Same as transaction capital gain 