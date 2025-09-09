"""
Test script to check URL display without terminal wrapping.
"""

import sys
import os
sys.path.append(r'c:\Users\User\CascadeProjects\find_duplicate_response')

import model

def test_url_display():
    """Test URL display without terminal wrapping."""
    file_path = r'c:\Users\User\CascadeProjects\find_duplicate_response\res\requests_08_26_06.06.2025.csv'
    
    try:
        rows = model.read_csv(file_path)
        print(f"Total rows read: {len(rows)}")
        
        # Find some longer URLs
        long_urls = []
        for row in rows:
            url = row.get('URL', '')
            if len(url) > 70:  # URLs longer than 70 characters
                long_urls.append(url)
                if len(long_urls) >= 5:  # Only collect first 5
                    break
        
        print("\nLong URLs found:")
        for i, url in enumerate(long_urls, 1):
            print(f"{i}. Length: {len(url)} characters")
            print(f"   URL: {url}")
            print(f"   Display test: {url:<150}")  # Test formatting
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_display()
