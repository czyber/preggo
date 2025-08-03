#!/usr/bin/env python3
"""
Script to show combined frontend and backend logs from dev.log file
"""

import os
import sys
from collections import deque


def main():
    try:
        limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    except (IndexError, ValueError):
        limit = 50
    
    # Path to dev.log file (in project root)
    dev_log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dev.log')
    
    try:
        if not os.path.exists(dev_log_path):
            print("No logs found. (dev.log file does not exist)")
            return
        
        # Read the last N lines from the file
        with open(dev_log_path, 'r', encoding='utf-8') as f:
            lines = deque(f, maxlen=limit)
        
        if not lines:
            print("No logs found.")
            return
        
        print(f"Showing last {len(lines)} logs:")
        print("-" * 80)
        
        for line in lines:
            # Remove trailing newline and print
            print(line.rstrip())
            
    except Exception as e:
        print(f"Error reading logs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()