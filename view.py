"""Module for displaying results in console."""

from typing import Dict, Any, List


def print_results(total: int, duplicates_count: int, duplicates: Dict[str, List[Dict[str, Any]]], stats: Dict[str, Dict[str, int]]) -> None:
    """
    Print processing results, including duplicates.
    
    Args:
        total (int): Total number of processed rows
        duplicates_count (int): Number of duplicates found
        duplicates (Dict[str, List[Dict[str, Any]]]): Dictionary with duplicate entries
        stats (Dict[str, Dict[str, int]]): Dictionary with statistics
    """
    # Colors for light background for better readability
    reset = '\033[0m'
    overall_color = '\033[92m' if duplicates_count == 0 else '\033[91m'  # Green or red

    # Light colors for duplicates (soft shades for light background)
    colors = [
        '\033[94m',   # Light blue
        '\033[92m',   # Light green
        '\033[93m',   # Light yellow
        '\033[95m',   # Light purple
        '\033[96m',   # Light cyan
        '\033[91m',   # Light red
        '\033[90m',   # Dark gray (still visible on light background)
        '\033[37m'    # White
    ]
    
    # Special colors for error codes
    error_4xx_color = '\033[91m'  # Light red for 4xx errors
    error_5xx_color = '\033[95m'  # Light purple for 5xx errors

    print(f"\n{overall_color}Processing statistics:{reset}")
    print(f"Processed rows: {total}")
    print(f"Duplicates found: {duplicates_count}")

    if duplicates:
        print(f"\n{overall_color}Duplicate rows:{reset}")
        print(f"{'Response code':<15} | {'Start time':<25} | {'Method':<7} | {'URL':<150} |")

        groups = list(duplicates.keys())
        for group_index, key in enumerate(groups):
            color = colors[group_index % len(colors)]
            for row in duplicates[key]:
                # Apply special coloring for error codes
                code = row['Response Code']
                if code.startswith('4') or code.startswith('5'):
                    if code.startswith('4'):
                        color = error_4xx_color
                    elif code.startswith('5'):
                        color = error_5xx_color
                
                # Apply color to row
                print(f"{color}"
                      f"{row['Response Code']:<15} | "
                      f"{row.get('Request Start Time', '')[:25]:<25} | "
                      f"{row['Method']:<7} | "
                      f"{row['URL']:<150} | "
                      f"{reset}")


def print_no_duplicates() -> None:
    """Print message that no duplicates were found."""
    print("\033[92mNo duplicates found\033[0m")