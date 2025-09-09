"""
Unit tests for the duplicate finder application.
"""

import unittest
import tempfile
import os
from model import read_csv, find_duplicates, get_stats


class TestModel(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary CSV file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='')
        self.temp_file.write('URL,Status,Response Code,Protocol,Method,Content-Type,Client Address,Client Port,Remote Address,Remote Port,Exception,Request Start Time,Request End Time,Response Start Time,Response End Time,Duration (ms),DNS Duration (ms),Connect Duration (ms),SSL Duration (ms),Request Duration (ms),Response Duration (ms),Latency (ms),Speed (KB/s),Request Speed (KB/s),Response Speed (KB/s),Request Handshake Size (bytes),Request Header Size (bytes),Request Body Size (bytes),Response Handshake Size (bytes),Response Header Size (bytes),Response Body Size (bytes),Request Compression,Response Compression\n')
        # Note: The read_csv function skips the header row, so we need extra rows for testing
        self.temp_file.write('http://example.com,COMPLETE,200,HTTP,GET,text/html,127.0.0.1,8080,192.168.1.1,80,,2025-01-01 10:00:00,2025-01-01 10:00:01,2025-01-01 10:00:01,2025-01-01 10:00:01,100,0,50,0,25,25,50,1000,500,500,100,200,300,,\n')
        self.temp_file.write('http://example.com,COMPLETE,200,HTTP,GET,text/html,127.0.0.1,8080,192.168.1.1,80,,2025-01-01 10:00:02,2025-01-01 10:00:03,2025-01-01 10:00:03,2025-01-01 10:00:03,100,0,50,0,25,25,50,1000,500,500,100,200,300,,\n')  # Duplicate
        self.temp_file.write('http://example.com,COMPLETE,200,HTTP,POST,text/html,127.0.0.1,8080,192.168.1.1,80,,2025-01-01 10:00:04,2025-01-01 10:00:05,2025-01-01 10:00:05,2025-01-01 10:00:05,100,0,50,0,25,25,50,1000,500,500,100,200,300,,\n')  # Different method
        self.temp_file.write('http://example.com,ERROR,404,HTTP,GET,text/html,127.0.0.1,8080,192.168.1.1,80,,2025-01-01 10:00:06,2025-01-01 10:00:07,2025-01-01 10:00:07,2025-01-01 10:00:07,100,0,50,0,25,25,50,1000,500,500,100,200,300,,\n')  # Different code/status
        self.temp_file.write('http://example.com,COMPLETE,200,HTTP,GET,text/html,127.0.0.1,8080,192.168.1.1,80,,2025-01-01 10:00:08,2025-01-01 10:00:09,2025-01-01 10:00:09,2025-01-01 10:00:09,100,0,50,0,25,25,50,1000,500,500,100,200,300,,\n')  # Another duplicate
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up the temporary file."""
        os.unlink(self.temp_file.name)
        
    def test_read_csv(self):
        """Test reading CSV file."""
        rows = read_csv(self.temp_file.name)
        # Should read 4 rows (header skipped, first data row skipped by next(), 4 remaining rows)
        self.assertEqual(len(rows), 4)
        if rows:
            self.assertEqual(rows[0]['URL'], 'http://example.com')
            self.assertEqual(rows[0]['Method'], 'GET')
        
    def test_find_duplicates(self):
        """Test finding duplicate entries."""
        rows = read_csv(self.temp_file.name)
        duplicates = find_duplicates(rows)
        # Should have one duplicate key with count of 2 (2 rows with same URL, Method, Code, Status)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(list(duplicates.values())[0], 2)
        
    def test_get_stats(self):
        """Test getting statistics."""
        rows = read_csv(self.temp_file.name)
        stats = get_stats(rows)
        self.assertIn('codes', stats)
        self.assertIn('methods', stats)
        self.assertEqual(stats['codes']['200'], 3)
        self.assertEqual(stats['codes']['404'], 1)
        self.assertEqual(stats['methods']['GET'], 3)
        self.assertEqual(stats['methods']['POST'], 1)


if __name__ == '__main__':
    unittest.main()