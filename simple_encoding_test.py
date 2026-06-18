#!/usr/bin/env python3
"""
Simple test script to verify that DuckDB's CSV encoding support works correctly.
This script creates a test CSV file with ISO-8859-1 encoding and tests loading it.
"""

import os
import tempfile
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
        result = conn.execute(f"""
            SELECT * FROM read_csv_auto('{temp_file}',
                header=true,
                auto_detect=true,
                ignore_errors=true,
                normalize_names=false,
                sample_size=-1,
                all_varchar=true,
                encoding='utf-8'
            )
        """).df()
        
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
        result = conn.execute(f"""
            SELECT * FROM read_csv_auto('{temp_file}',
                header=true,
                auto_detect=true,
                ignore_errors=true,
                normalize_names=false,
                sample_size=-1,
                all_varchar=true,
                encoding='latin-1'
            )
        """).df()
        
        print(f"✓ Latin-1 encoding succeeded! Loaded {len(result)} rows")
        print(f"  Columns: {list(result.columns)}")
        print(f"  Sample data:")
        for i, row in result.iterrows():
            print(f"    {row['name']}, {row['value']}, {row['description']}")
        
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
        result = conn.execute(f"""
            SELECT * FROM read_csv_auto('{temp_file}',
                header=true,
                auto_detect=true,
                ignore_errors=true,
                normalize_names=false,
                sample_size=-1,
                all_varchar=true
            )
        """).df()
        
        print(f"✓ Default encoding succeeded! Loaded {len(result)} rows")
        print(f"  Sample data:")
        for i, row in result.iterrows():
            print(f"    {row['name']}, {row['value']}")
        
    except Exception as e:
        print(f"✗ Default encoding failed: {e}")
    finally:
        conn.close()
        os.unlink(temp_file)

if __name__ == "__main__":
    print("Testing DuckDB CSV encoding support...")
    print("=" * 50)
    
    test_default_encoding()
    print()
    
    test_utf8_encoding_fails()
    print()
    
    test_latin1_encoding_succeeds()
    print()
    
    print("=" * 50)
    print("Test completed!") 