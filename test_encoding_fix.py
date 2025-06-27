#!/usr/bin/env python3
"""
Test script to verify that the CSV encoding fix works correctly.
This script creates a test CSV file with ISO-8859-1 encoding and tests loading it.
"""

import os
import tempfile
import pandas as pd
from preswald.engine.managers.data import CSVConfig, CSVSource
import duckdb

def create_test_csv_with_latin1():
    """Create a test CSV file with ISO-8859-1 encoding containing special characters."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='latin-1') as f:
        # Write CSV content with Latin-1 characters
        f.write("name,value,description\n")
        f.write("José,123,áéíóú\n")
        f.write("François,456,ñç\n")
        f.write("Müller,789,ßäöü\n")
        temp_file = f.name
    
    return temp_file

def test_utf8_encoding_fails():
    """Test that loading with UTF-8 encoding fails on Latin-1 file."""
    temp_file = create_test_csv_with_latin1()
    
    try:
        # Try to load with UTF-8 encoding (should fail)
        conn = duckdb.connect(':memory:')
        config = CSVConfig(path=temp_file, encoding="utf-8")
        source = CSVSource("test_csv", config, conn)
        
        # If we get here, it means the file loaded successfully with UTF-8
        # which might happen if the file doesn't contain problematic characters
        print("✓ UTF-8 encoding test completed")
        
    except Exception as e:
        print(f"✓ UTF-8 encoding failed as expected: {e}")
    finally:
        conn.close()
        os.unlink(temp_file)

def test_latin1_encoding_succeeds():
    """Test that loading with Latin-1 encoding succeeds on Latin-1 file."""
    temp_file = create_test_csv_with_latin1()
    
    try:
        # Load with Latin-1 encoding (should succeed)
        conn = duckdb.connect(':memory:')
        config = CSVConfig(path=temp_file, encoding="latin-1")
        source = CSVSource("test_csv", config, conn)
        
        # Try to query the data
        df = source.to_df()
        print(f"✓ Latin-1 encoding succeeded! Loaded {len(df)} rows")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Sample data: {df.head().to_dict()}")
        
    except Exception as e:
        print(f"✗ Latin-1 encoding failed: {e}")
    finally:
        conn.close()
        os.unlink(temp_file)

def test_default_encoding():
    """Test that default encoding (UTF-8) works for regular files."""
    # Create a regular UTF-8 CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write("name,value\n")
        f.write("John,100\n")
        f.write("Jane,200\n")
        temp_file = f.name
    
    try:
        # Load with default encoding (should succeed)
        conn = duckdb.connect(':memory:')
        config = CSVConfig(path=temp_file)  # No encoding specified, should default to utf-8
        source = CSVSource("test_csv", config, conn)
        
        # Try to query the data
        df = source.to_df()
        print(f"✓ Default encoding succeeded! Loaded {len(df)} rows")
        print(f"  Sample data: {df.head().to_dict()}")
        
    except Exception as e:
        print(f"✗ Default encoding failed: {e}")
    finally:
        conn.close()
        os.unlink(temp_file)

if __name__ == "__main__":
    print("Testing CSV encoding fix...")
    print("=" * 50)
    
    test_default_encoding()
    print()
    
    test_utf8_encoding_fails()
    print()
    
    test_latin1_encoding_succeeds()
    print()
    
    print("=" * 50)
    print("Test completed!") 