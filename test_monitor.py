#!/usr/bin/env python3
"""
Test script for NYC Property Violation Monitor
Use this to test the system before setting up daily monitoring
"""

import json
import sys
from violation_monitor import ViolationMonitor, NYCDataFetcher
from datetime import datetime, timedelta

def test_api_connectivity():
    """Test NYC Open Data API connectivity"""
    print("Testing NYC Open Data API connectivity...")
    
    fetcher = NYCDataFetcher()
    
    # Test with a sample request (get one record from each dataset)
    test_params = {'$limit': 1}
    
    datasets = {
        '311 Complaints': 'erm2-nwe9',
        'HPD Violations': 'wvxf-dwi5',
        'OATH Violations': '6bgk-3dad',
        'DOB Violations': '3h2n-5cm9'
    }
    
    for name, dataset_id in datasets.items():
        try:
            result = fetcher._make_request(dataset_id, test_params)
            if result:
                print(f"✓ {name}: Connected successfully")
            else:
                print(f"✗ {name}: No data returned")
        except Exception as e:
            print(f"✗ {name}: Error - {e}")

def test_property_data(block: str, lot: str):
    """Test fetching data for a specific property"""
    print(f"\nTesting data fetch for Block {block}, Lot {lot}...")
    
    fetcher = NYCDataFetcher()
    
    # Get data from the last 30 days
    since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Test each data source
    print(f"Looking for violations since {since_date}")
    
    # 311 Complaints
    try:
        complaints = fetcher.get_311_complaints(block, lot, since_date)
        print(f"✓ 311 Complaints: {len(complaints)} found")
        if complaints:
            print(f"  Latest: {complaints[0].get('created_date', 'N/A')} - {complaints[0].get('complaint_type', 'N/A')}")
    except Exception as e:
        print(f"✗ 311 Complaints: Error - {e}")
    
    # HPD Violations
    try:
        hpd_violations = fetcher.get_hpd_violations(block, lot, since_date)
        print(f"✓ HPD Violations: {len(hpd_violations)} found")
        if hpd_violations:
            print(f"  Latest: {hpd_violations[0].get('inspectiondate', 'N/A')} - {hpd_violations[0].get('violationtype', 'N/A')}")
    except Exception as e:
        print(f"✗ HPD Violations: Error - {e}")
    
    # OATH Violations
    try:
        oath_violations = fetcher.get_oath_violations(block, lot, since_date)
        print(f"✓ OATH Violations: {len(oath_violations)} found")
        if oath_violations:
            print(f"  Latest: {oath_violations[0].get('hearing_date', 'N/A')} - {oath_violations[0].get('violation_type', 'N/A')}")
    except Exception as e:
        print(f"✗ OATH Violations: Error - {e}")
    
    # DOB Violations
    try:
        dob_violations = fetcher.get_dob_violations(block, lot, since_date)
        print(f"✓ DOB Violations: {len(dob_violations)} found")
        if dob_violations:
            print(f"  Latest: {dob_violations[0].get('issue_date', 'N/A')} - {dob_violations[0].get('violation_type_code', 'N/A')}")
    except Exception as e:
        print(f"✗ DOB Violations: Error - {e}")

def test_email_config():
    """Test email configuration"""
    print("\nTesting email configuration...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        email_config = config.get('email', {})
        required_fields = ['smtp_server', 'smtp_port', 'from_email', 'from_password', 'to_emails']
        
        for field in required_fields:
            if field in email_config and email_config[field]:
                print(f"✓ {field}: Configured")
            else:
                print(f"✗ {field}: Missing or empty")
                
        # Check if to_emails is a list
        if isinstance(email_config.get('to_emails'), list):
            print(f"✓ to_emails: {len(email_config['to_emails'])} recipients configured")
        else:
            print("✗ to_emails: Should be a list of email addresses")
            
    except FileNotFoundError:
        print("✗ config.json not found. Please copy config.json.example to config.json and configure it.")
    except json.JSONDecodeError:
        print("✗ config.json is not valid JSON")
    except Exception as e:
        print(f"✗ Error reading config: {e}")

def test_full_run():
    """Test a full monitoring run (without sending email)"""
    print("\nTesting full monitoring run...")
    
    try:
        monitor = ViolationMonitor()
        print("✓ ViolationMonitor initialized successfully")
        
        # Test database initialization
        print("✓ Database initialized")
        
        # Test violation check (dry run)
        print("Running violation check (this may take a moment)...")
        monitor.check_violations()
        print("✓ Violation check completed")
        
    except FileNotFoundError:
        print("✗ config.json not found. Please copy config.json.example to config.json and configure it.")
    except Exception as e:
        print(f"✗ Error during full run: {e}")

def main():
    """Main test function"""
    print("NYC Property Violation Monitor - Test Suite")
    print("=" * 50)
    
    # Test API connectivity
    test_api_connectivity()
    
    # Test email configuration
    test_email_config()
    
    # Test with property from config if available
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        block = config['property']['block']
        lot = config['property']['lot']
        test_property_data(block, lot)
    except:
        print("\nSkipping property data test - config.json not found or invalid")
        print("To test with specific property, configure config.json and run again")
    
    # Test full run
    test_full_run()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNext steps:")
    print("1. Configure config.json with your property and email settings")
    print("2. Test email sending by running the monitor once manually")
    print("3. Set up daily automation using cron or the scheduler.py script")

if __name__ == "__main__":
    main()
