"""
Test script to verify that the API displays full URLs.
"""

import requests

def test_api_url_length():
    """Test that the API displays full URLs without truncation."""
    url = 'http://localhost:5000/find-duplicates'
    
    # Path to the test CSV file
    file_path = r'c:\Users\User\CascadeProjects\find_duplicate_response\res\requests_08_26_06.06.2025.csv'
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            data = response.json()
            print("API Response:")
            print(f"Total rows: {data.get('total_rows', 0)}")
            print(f"Duplicates count: {data.get('duplicates_count', 0)}")
            print(f"Duplicate groups: {data.get('duplicate_groups', 0)}")
            
            # Check if duplicates exist and examine URL length
            duplicates = data.get('duplicates', {})
            if duplicates:
                print("\nSample duplicate entries:")
                for i, (key, rows) in enumerate(duplicates.items()):
                    if i >= 3:  # Only show first 3 groups
                        break
                    print(f"\nGroup {i+1}:")
                    for j, row in enumerate(rows):
                        if j >= 2:  # Only show first 2 rows per group
                            break
                        url = row.get('URL', '')
                        print(f"  URL length: {len(url)} characters")
                        print(f"  URL: {url}")
                        if len(url) > 100:
                            print("  [URL is displayed with full length]")
                    print("  ---")
            else:
                print("No duplicates found in the test data.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api_url_length()
