"""
Test script to verify that we're reading full URLs from the CSV file.
"""

import sys
import os
sys.path.append(r'c:\Users\User\CascadeProjects\find_duplicate_response')

import model

def test_csv_reading():
    """Test that we're reading full URLs from the CSV file."""
    file_path = r'c:\Users\User\CascadeProjects\find_duplicate_response\res\requests_08_26_06.06.2025.csv'
    
    try:
        rows = model.read_csv(file_path)
        print(f"Total rows read: {len(rows)}")
        
        # Check the first few rows for URL lengths
        print("\nFirst few rows:")
        for i, row in enumerate(rows[:5]):
            url = row.get('URL', '')
            print(f"  Row {i+1}:")
            print(f"    URL length: {len(url)}")
            print(f"    Full URL: {url}")
            if len(url) > 100:
                print("    [This is a long URL]")
            print()
            
    except Exception as e:
        print(f"Error reading CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_reading()
