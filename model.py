"""Data model for processing CSV files and finding duplicates."""

import csv
import urllib.parse
from typing import List, Dict, Any, TextIO, Set
from collections import defaultdict


# Required fields for CSV processing
REQUIRED_FIELDS: Set[str] = {'URL', 'Method', 'Response Code', 'Status'}


def read_csv(file_path: str, skip_header: bool = True) -> List[Dict[str, Any]]:
    """
    Read CSV file and return list of rows as dictionaries.
    
    Args:
        file_path (str): Path to CSV file
        skip_header (bool): Whether to skip header row
        
    Returns:
        List[Dict[str, Any]]: List of row dictionaries
        
    Raises:
        ValueError: If file reading fails or required fields are missing
        FileNotFoundError: If file doesn't exist
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            return _read_csv_file(file, skip_header, REQUIRED_FIELDS)
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")


def read_csv_from_string(file_buffer: TextIO, skip_header: bool = True) -> List[Dict[str, Any]]:
    """
    Read CSV data from string buffer and return list of rows as dictionaries.
    
    Args:
        file_buffer (TextIO): String buffer with CSV data
        skip_header (bool): Whether to skip header row
        
    Returns:
        List[Dict[str, Any]]: List of row dictionaries
        
    Raises:
        ValueError: If file reading fails or required fields are missing
    """
    return _read_csv_file(file_buffer, skip_header, REQUIRED_FIELDS)


def _read_csv_file(file_obj: TextIO, skip_header: bool, required_fields: Set[str]) -> List[Dict[str, Any]]:
    """
    Internal function to read CSV from file object.
    
    Args:
        file_obj (TextIO): File object to read from
        skip_header (bool): Whether to skip header row
        required_fields (Set[str]): Set of required fields
        
    Returns:
        List[Dict[str, Any]]: List of row dictionaries
    """
    csv_reader = csv.DictReader(file_obj)
    
    # Skip header if required
    if skip_header:
        try:
            next(csv_reader)
        except StopIteration:
            return []  # Empty file

    rows: List[Dict[str, Any]] = []
    for idx, row in enumerate(csv_reader, 1):
        if not row:
            continue
            
        # Check for required fields
        if not all(field in row for field in required_fields):
            raise ValueError(f"Row {idx}: Missing required fields")
            
        rows.append(row)
        
    return rows


def _normalize_url_for_comparison(url: str) -> str:
    """
    Normalize URL for comparison, including ordering query parameters.
    
    Args:
        url (str): URL to normalize
        
    Returns:
        str: Normalized URL with ordered query parameters
    """
    try:
        # Parse URL into components
        parsed = urllib.parse.urlparse(url)
        
        # If there are query parameters, sort them for consistent comparison
        if parsed.query:
            # Parse query parameters
            query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            # Sort parameters by key
            sorted_params = sorted(query_params.items())
            # Form sorted query string
            normalized_query = urllib.parse.urlencode(sorted_params, doseq=True)
            # Build normalized URL
            normalized_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                normalized_query,
                parsed.fragment
            ))
            return normalized_url
        else:
            # If no query parameters, return original URL
            return url
    except Exception:
        # In case of error, return original URL
        return url


def _create_comparison_key(row: Dict[str, Any]) -> str:
    """
    Create key for comparing records.
    
    Args:
        row (Dict[str, Any]): Dictionary with row data
        
    Returns:
        str: Key for comparing records
    """
    # Normalize URL for exact comparison with query parameters
    normalized_url = _normalize_url_for_comparison(row['URL'])
    
    # Create key from all critical fields
    key_parts = [
        normalized_url,
        str(row['Method']),
        str(row['Response Code']),
        str(row['Status'])
    ]
    
    return '-'.join(key_parts)


def find_duplicates(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Find duplicate records based on URL, method, response code, and status.
    When comparing URLs, query parameters are considered with normalization.
    
    Args:
        rows (List[Dict[str, Any]]): List of row dictionaries
        
    Returns:
        Dict[str, int]: Dictionary with duplicate keys and their counts
    """
    count: Dict[str, int] = defaultdict(int)
    
    for row in rows:
        # Create normalized key for comparison
        key = _create_comparison_key(row)
        count[key] += 1
        
    return {k: v for k, v in count.items() if v > 1}


def get_stats(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Get statistics on response codes and methods.
    
    Args:
        rows (List[Dict[str, Any]]): List of row dictionaries
        
    Returns:
        Dict[str, Dict[str, int]]: Dictionary with counts of codes and methods
    """
    code_counts: Dict[str, int] = defaultdict(int)
    method_counts: Dict[str, int] = defaultdict(int)
    
    for row in rows:
        code = row.get('Response Code', 'No code')
        method = row.get('Method', 'No method')
        
        code_counts[code] += 1
        method_counts[method] += 1
        
    return {'codes': dict(code_counts), 'methods': dict(method_counts)}