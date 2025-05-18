import os
from click.testing import CliRunner
from capgains.cli import capgains
from capgains.transactions_reader import TransactionsReader


def test_sample_files_exist():
    """Verify that both sample files exist in the tests directory."""
    assert os.path.exists(os.path.join('tests', 'sample.csv'))
    assert os.path.exists(os.path.join('tests', 'sample.json'))


def test_can_read_sample_files():
    """Verify that we can read and parse both sample files."""
    # Test CSV file
    csv_transactions = TransactionsReader.get_transactions(
        os.path.join('tests', 'sample.csv')
    )
    assert len(csv_transactions) == 36

    # Test JSON file
    json_transactions = TransactionsReader.get_transactions(
        os.path.join('tests', 'sample.json')
    )
    assert len(json_transactions) == 36

    # Verify both files produce identical results
    for csv_t, json_t in zip(csv_transactions, json_transactions):
        assert csv_t.__dict__ == json_t.__dict__

    # Verify we have the expected tickers
    expected_tickers = {
        'AAPL', 'GOOGL', 'TD.TO', 'RY.TO', 'VFV.TO', 'MSFT', 'SHOP.TO'
    }
    assert set(csv_transactions.tickers) == expected_tickers
    assert set(json_transactions.tickers) == expected_tickers

    # Verify we have both currencies
    currencies = {t.currency for t in csv_transactions}
    assert currencies == {'USD', 'CAD'}

    # Verify we have transactions across all years
    years = {t.date.year for t in csv_transactions}
    assert years == {2022, 2023, 2024}


def test_maxcost_sample_2022():
    """Test the maxcost command with both sample files for 2022."""
    runner = CliRunner()

    # Test CSV input
    csv_result = runner.invoke(
        capgains, ['maxcost', os.path.join('tests', 'sample.csv'), '2022']
    )
    assert csv_result.exit_code == 0

    # Test JSON input
    json_result = runner.invoke(
        capgains, ['maxcost', os.path.join('tests', 'sample.json'), '2022']
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert 'AAPL-2022' in csv_result.output
    assert 'GOOGL-2022' in csv_result.output
    assert 'TD.TO-2022' in csv_result.output
    assert 'VFV.TO-2022' in csv_result.output
    assert 'Max cost =' in csv_result.output
    assert 'Year end =' in csv_result.output


def test_maxcost_sample_2023():
    """Test the maxcost command with both sample files for 2023."""
    runner = CliRunner()

    # Test CSV input
    csv_result = runner.invoke(
        capgains, ['maxcost', os.path.join('tests', 'sample.csv'), '2023']
    )
    assert csv_result.exit_code == 0

    # Test JSON input
    json_result = runner.invoke(
        capgains, ['maxcost', os.path.join('tests', 'sample.json'), '2023']
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert 'AAPL-2023' in csv_result.output
    assert 'GOOGL-2023' in csv_result.output
    assert 'TD.TO-2023' in csv_result.output
    assert 'RY.TO-2023' in csv_result.output
    assert 'VFV.TO-2023' in csv_result.output


def test_maxcost_sample_2024():
    """Test the maxcost command with both sample files for 2024."""
    runner = CliRunner()

    # Test CSV input
    csv_result = runner.invoke(
        capgains, ['maxcost', os.path.join('tests', 'sample.csv'), '2024']
    )
    assert csv_result.exit_code == 0

    # Test JSON input
    json_result = runner.invoke(
        capgains, ['maxcost', os.path.join('tests', 'sample.json'), '2024']
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert 'AAPL-2024' in csv_result.output
    assert 'MSFT-2024' in csv_result.output
    assert 'SHOP.TO-2024' in csv_result.output
    assert 'VFV.TO-2024' in csv_result.output


def test_calc_sample_2022():
    """Test the calc command with both sample files for 2022."""
    runner = CliRunner()

    # Test CSV input
    csv_result = runner.invoke(
        capgains, ['calc', os.path.join('tests', 'sample.csv'), '2022']
    )
    assert csv_result.exit_code == 0

    # Test JSON input
    json_result = runner.invoke(
        capgains, ['calc', os.path.join('tests', 'sample.json'), '2022']
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert 'AAPL-2022' in csv_result.output
    assert 'GOOGL-2022' in csv_result.output
    assert 'TD.TO-2022' in csv_result.output
    assert 'VFV.TO-2022' in csv_result.output
    assert 'Total Gains' in csv_result.output


def test_calc_sample_2023():
    """Test the calc command with both sample files for 2023."""
    runner = CliRunner()

    # Test CSV input
    csv_result = runner.invoke(
        capgains, ['calc', os.path.join('tests', 'sample.csv'), '2023']
    )
    assert csv_result.exit_code == 0

    # Test JSON input
    json_result = runner.invoke(
        capgains, ['calc', os.path.join('tests', 'sample.json'), '2023']
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert 'AAPL-2023' in csv_result.output
    assert 'GOOGL-2023' in csv_result.output
    assert 'TD.TO-2023' in csv_result.output
    assert 'RY.TO-2023' in csv_result.output
    assert 'VFV.TO-2023' in csv_result.output
    assert 'Total Gains' in csv_result.output


def test_calc_sample_2024():
    """Test the calc command with both sample files for 2024."""
    runner = CliRunner()

    # Test CSV input
    csv_result = runner.invoke(
        capgains, ['calc', os.path.join('tests', 'sample.csv'), '2024']
    )
    assert csv_result.exit_code == 0

    # Test JSON input
    json_result = runner.invoke(
        capgains, ['calc', os.path.join('tests', 'sample.json'), '2024']
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert 'AAPL-2024' in csv_result.output
    assert 'MSFT-2024' in csv_result.output
    assert 'SHOP.TO-2024' in csv_result.output
    assert 'VFV.TO-2024' in csv_result.output
    assert 'Total Gains' in csv_result.output


def test_show_sample():
    """Test the show command with both sample files."""
    runner = CliRunner()

    # Test showing all transactions from CSV
    csv_result = runner.invoke(
        capgains, ['show', os.path.join('tests', 'sample.csv')]
    )
    assert csv_result.exit_code == 0

    # Test showing all transactions from JSON
    json_result = runner.invoke(
        capgains, ['show', os.path.join('tests', 'sample.json')]
    )
    assert json_result.exit_code == 0

    # Verify both formats produce identical results
    assert csv_result.output == json_result.output

    # Verify expected content
    assert '2022' in csv_result.output
    assert '2023' in csv_result.output
    assert '2024' in csv_result.output

    # Test filtering by ticker with both formats
    csv_filtered = runner.invoke(
        capgains, ['show', os.path.join('tests', 'sample.csv'), '-t', 'AAPL']
    )
    json_filtered = runner.invoke(
        capgains, ['show', os.path.join('tests', 'sample.json'), '-t', 'AAPL']
    )
    assert csv_filtered.exit_code == 0
    assert json_filtered.exit_code == 0
    assert csv_filtered.output == json_filtered.output
    assert 'AAPL' in csv_filtered.output
    assert 'GOOGL' not in csv_filtered.output

    # Test showing exchange rates with both formats
    csv_rates = runner.invoke(
        capgains, ['show', os.path.join('tests', 'sample.csv'), '-e']
    )
    json_rates = runner.invoke(
        capgains, ['show', os.path.join('tests', 'sample.json'), '-e']
    )
    assert csv_rates.exit_code == 0
    assert json_rates.exit_code == 0
    assert csv_rates.output == json_rates.output
    assert 'exchange' in csv_rates.output
