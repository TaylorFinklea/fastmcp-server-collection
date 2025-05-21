#!/usr/bin/env python
"""
fastmcp-server-collection - Run FastMCP servers
"""

import argparse
import sys

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run FastMCP servers")
  parser.add_argument("-s", "--server", required=True, help="Server to run")
  args = parser.parse_args()
  
  print(f"Starting {args.server} server...")
  # TODO: Implement server loading logic
