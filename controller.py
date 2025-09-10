"""Main controller for the duplicate finder application."""

import argparse
import logging
import sys
import os
from typing import Optional, Dict, Any, List

from model import read_csv, find_duplicates, get_stats, _create_comparison_key
from view import print_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default file path - using relative path for portability
DEFAULT_CSV_FILE_PATH: str = os.path.join("res", "requests_08_26_06.06.2025.csv")


def main(file_path: Optional[str] = None) -> int:
    """
    Main application function.
    
    Args:
        file_path (Optional[str]): Path to CSV file to process
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Use default path if no other path is specified
    if file_path is None:
        file_path = DEFAULT_CSV_FILE_PATH
    
    try:
        rows = read_csv(file_path)
        
        # Check for empty data
        if not rows:
            print("Error: File is empty")
            return 1

        total = len(rows)
        duplicates_info = find_duplicates(rows)
        stats = get_stats(rows)
        duplicates_count = sum(v - 1 for v in duplicates_info.values())

        # Group duplicate rows
        duplicates_full: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            # Use the same key creation function as in the model for proper grouping
            key = _create_comparison_key(row)
            if key in duplicates_info:
                if key not in duplicates_full:
                    duplicates_full[key] = []
                duplicates_full[key].append(row)

        print_results(total, duplicates_count, duplicates_full, stats)
        return 0

    except ValueError as e:
        print(f"Data error: {str(e)}")
        logger.error(f"Data error: {str(e)}")
        return 1
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        logger.error(f"CRITICAL ERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Find duplicate entries in CSV log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default file
  %(prog)s path/to/your/file.csv     # Specify file
        """
    )
    
    parser.add_argument(
        "file_path", 
        nargs="?", 
        default=DEFAULT_CSV_FILE_PATH,
        help="Path to CSV file to process (default: {})".format(DEFAULT_CSV_FILE_PATH)
    )
    
    args = parser.parse_args()
    sys.exit(main(args.file_path))