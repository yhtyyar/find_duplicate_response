"""
Check the actual URL lengths in the API JSON response.
"""

import requests
import json

def check_url_lengths():
    """Check the actual URL lengths in the API JSON response."""
    url = 'http://localhost:5000/find-duplicates'
    
    # Path to the test CSV file
    file_path = r'c:\Users\User\CascadeProjects\find_duplicate_response\res\requests_08_26_06.06.2025.csv'
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            data = response.json()
            
            # Check if duplicates exist and examine URL length
            duplicates = data.get('duplicates', {})
            if duplicates:
                print("Actual URL lengths in JSON response:")
                for i, (key, rows) in enumerate(duplicates.items()):
                    if i >= 3:  # Only show first 3 groups
                        break
                    print(f"\nGroup {i+1}:")
                    for j, row in enumerate(rows):
                        if j >= 2:  # Only show first 2 rows per group
                            break
                        url = row.get('URL', '')
                        print(f"  URL length: {len(url)} characters")
                        print(f"  Full URL: {url}")
                    print("  ---")
            else:
                print("No duplicates found in the test data.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    check_url_lengths()
