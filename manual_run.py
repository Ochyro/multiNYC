#!/usr/bin/env python3
"""
Manual run script for NYC Property Violation Monitor
Use this to manually check for violations without waiting for the scheduled run
"""

import sys
import argparse
from violation_monitor import ViolationMonitor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Manual run with optional parameters"""
    parser = argparse.ArgumentParser(description='Manually run NYC Property Violation Monitor')
    parser.add_argument('--block', help='Override block number from config')
    parser.add_argument('--lot', help='Override lot number from config')
    parser.add_argument('--no-email', action='store_true', help='Skip sending email notification')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize monitor
        monitor = ViolationMonitor()
        
        # Override block/lot if provided
        if args.block:
            monitor.block = args.block
            logger.info(f"Overriding block to: {args.block}")
        if args.lot:
            monitor.lot = args.lot
            logger.info(f"Overriding lot to: {args.lot}")
        
        # Temporarily disable email if requested
        if args.no_email:
            logger.info("Email notification disabled for this run")
            monitor.notifier.to_emails = []
        
        # Run the check
        logger.info("Starting manual violation check...")
        monitor.check_violations()
        logger.info("Manual violation check completed")
        
    except KeyboardInterrupt:
        logger.info("Manual run interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during manual run: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
