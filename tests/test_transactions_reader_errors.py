import pytest
from click import ClickException
from capgains.transactions_reader import TransactionsReader
import json
import os

def test_file_not_found():
    """Test handling of non-existent file."""
    with pytest.raises(ClickException, match="File not found:"):
        TransactionsReader.get_transactions("nonexistent.csv")

def test_file_not_readable(tmpdir):
    """Test handling of file that cannot be opened for reading."""
    test_file = tmpdir.join("unreadable.csv")
    test_file.write("some content")
    os.chmod(str(test_file), 0o000)  # Remove all permissions
    
    with pytest.raises(OSError, match="Could not open .* for reading"):
        TransactionsReader.get_transactions(str(test_file))
    
    os.chmod(str(test_file), 0o644)  # Restore permissions for cleanup

def test_invalid_json_format(tmpdir):
    """Test handling of invalid JSON format."""
    json_file = tmpdir.join("invalid.json")
    json_file.write("invalid json content")
    
    with pytest.raises(ClickException, match="Invalid JSON format in file:"):
        TransactionsReader.get_transactions(str(json_file))

def test_json_not_list(tmpdir):
    """Test handling of JSON that's not a list."""
    json_file = tmpdir.join("not_list.json")
    json_file.write(json.dumps({"not": "a list"}))
    
    with pytest.raises(ClickException, match="JSON file must contain a list of transactions"):
        TransactionsReader.get_transactions(str(json_file))

def test_json_extra_fields(tmpdir):
    """Test handling of JSON entry with extra fields."""
    json_file = tmpdir.join("extra_fields.json")
    entry = {
        "date": "2023-01-01",
        "description": "Test",
        "ticker": "TEST",
        "action": "BUY",
        "qty": "100",
        "price": "10.00",
        "commission": "1.00",
        "currency": "CAD",
        "extra_field": "should not be here"
    }
    json_file.write(json.dumps([entry]))
    
    with pytest.raises(ClickException, match="expected .* columns"):
        TransactionsReader.get_transactions(str(json_file))

def test_json_missing_fields(tmpdir):
    """Test handling of JSON entry with missing fields."""
    json_file = tmpdir.join("missing_fields.json")
    entry = {
        "date": "2023-01-01",
        "description": "Test",
        "ticker": "TEST",
        # missing action
        "qty": "100",
        "price": "10.00",
        "commission": "1.00",
        "currency": "CAD"
    }
    json_file.write(json.dumps([entry]))
    
    with pytest.raises(ClickException, match="missing required fields"):
        TransactionsReader.get_transactions(str(json_file))

def test_csv_header_detection(tmpdir):
    """Test detection and rejection of CSV header row."""
    csv_file = tmpdir.join("with_header.csv")
    csv_content = "Date,Description,Ticker,Action,Quantity,Price,Commission,Currency\n"
    csv_content += "2023-01-01,Test,TEST,BUY,100,10.00,1.00,CAD"
    csv_file.write(csv_content)
    
    with pytest.raises(ClickException, match="First row appears to be a header row"):
        TransactionsReader.get_transactions(str(csv_file))

def test_csv_wrong_column_count(tmpdir):
    """Test handling of CSV row with wrong number of columns."""
    csv_file = tmpdir.join("wrong_columns.csv")
    csv_content = "2023-01-01,Test,TEST,BUY,100,10.00,1.00"  # Missing currency
    csv_file.write(csv_content)
    
    with pytest.raises(ClickException, match="expected .* columns"):
        TransactionsReader.get_transactions(str(csv_file))

def test_invalid_numeric_values(tmpdir):
    """Test handling of invalid numeric values in both CSV and JSON."""
    # Test CSV
    csv_file = tmpdir.join("invalid_numbers.csv")
    csv_content = "2023-01-01,Test,TEST,BUY,not_a_number,10.00,1.00,CAD"
    csv_file.write(csv_content)
    
    with pytest.raises(ClickException, match="quantity entered .* is not a valid number"):
        TransactionsReader.get_transactions(str(csv_file))
    
    # Test JSON
    json_file = tmpdir.join("invalid_numbers.json")
    entry = {
        "date": "2023-01-01",
        "description": "Test",
        "ticker": "TEST",
        "action": "BUY",
        "qty": "not_a_number",
        "price": "10.00",
        "commission": "1.00",
        "currency": "CAD"
    }
    json_file.write(json.dumps([entry]))
    
    with pytest.raises(ClickException, match="quantity entered .* is not a valid number"):
        TransactionsReader.get_transactions(str(json_file))

def test_non_chronological_order(tmpdir):
    """Test handling of transactions not in chronological order."""
    # Test CSV
    csv_file = tmpdir.join("non_chrono.csv")
    csv_content = "2023-02-01,Test,TEST,BUY,100,10.00,1.00,CAD\n"
    csv_content += "2023-01-01,Test,TEST,BUY,100,10.00,1.00,CAD"
    csv_file.write(csv_content)
    
    with pytest.raises(ClickException, match="Transactions were not entered in chronological order"):
        TransactionsReader.get_transactions(str(csv_file))
    
    # Test JSON
    json_file = tmpdir.join("non_chrono.json")
    entries = [
        {
            "date": "2023-02-01",
            "description": "Test",
            "ticker": "TEST",
            "action": "BUY",
            "qty": "100",
            "price": "10.00",
            "commission": "1.00",
            "currency": "CAD"
        },
        {
            "date": "2023-01-01",
            "description": "Test",
            "ticker": "TEST",
            "action": "BUY",
            "qty": "100",
            "price": "10.00",
            "commission": "1.00",
            "currency": "CAD"
        }
    ]
    json_file.write(json.dumps(entries))
    
    with pytest.raises(ClickException, match="Transactions were not entered in chronological order"):
        TransactionsReader.get_transactions(str(json_file)) 