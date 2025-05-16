#!/usr/bin/env python3
"""
Scheduler for NYC Property Violation Monitor
Runs the violation monitor on a daily schedule
"""

import schedule
import time
import logging
from violation_monitor import ViolationMonitor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_violation_check():
    """Run the violation check"""
    logger.info("Starting scheduled violation check")
    try:
        monitor = ViolationMonitor()
        monitor.check_violations()
        logger.info("Scheduled violation check completed")
    except Exception as e:
        logger.error(f"Error during scheduled violation check: {e}")

def main():
    """Main scheduler function"""
    # Schedule the job to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(run_violation_check)
    
    logger.info("Violation monitor scheduler started - will run daily at 9:00 AM")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
