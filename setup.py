#!/usr/bin/env python3
"""
Setup script for NYC Property Violation Monitor
Helps with initial setup and configuration
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False
    return True

def setup_config():
    """Create config.json from template if it doesn't exist"""
    if os.path.exists('config.json'):
        print("✓ config.json already exists")
        return True
    
    if not os.path.exists('config.json.example'):
        print("✗ config.json.example not found")
        return False
    
    print("Creating config.json from template...")
    try:
        with open('config.json.example', 'r') as f:
            config = json.load(f)
        
        # Interactive configuration
        print("\nLet's configure your monitoring setup:")
        
        # Property configuration
        block = input(f"Enter Block number [{config['property']['block']}]: ").strip()
        if block:
            config['property']['block'] = block
        
        lot = input(f"Enter Lot number [{config['property']['lot']}]: ").strip()
        if lot:
            config['property']['lot'] = lot
        
        # Email configuration
        print("\nEmail Configuration:")
        from_email = input(f"From email address [{config['email']['from_email']}]: ").strip()
        if from_email:
            config['email']['from_email'] = from_email
        
        smtp_server = input(f"SMTP server [{config['email']['smtp_server']}]: ").strip()
        if smtp_server:
            config['email']['smtp_server'] = smtp_server
        
        smtp_port = input(f"SMTP port [{config['email']['smtp_port']}]: ").strip()
        if smtp_port:
            config['email']['smtp_port'] = int(smtp_port)
        
        # Get recipient emails
        to_emails = []
        print("Enter recipient email addresses (press enter when done):")
        while True:
            email = input("Email: ").strip()
            if not email:
                break
            to_emails.append(email)
        
        if to_emails:
            config['email']['to_emails'] = to_emails
        
        # Save configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✓ config.json created successfully")
        print("\nIMPORTANT: Don't forget to set your email password in config.json")
        print("For Gmail, use an App Password instead of your regular password.")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating config.json: {e}")
        return False

def setup_cron():
    """Provide instructions for setting up cron job"""
    print("\nSetting up daily automation...")
    print("You can choose one of these methods:")
    print("\n1. Using cron (Linux/Mac):")
    print("   Add this line to your crontab (run 'crontab -e'):")
    
    current_path = os.path.abspath('.')
    python_path = sys.executable
    
    print(f"   0 9 * * * cd {current_path} && {python_path} violation_monitor.py")
    print("   This will run the monitor daily at 9:00 AM")
    
    print("\n2. Using the Python scheduler:")
    print(f"   Run: {python_path} scheduler.py")
    print("   Keep this script running in the background")
    
    print("\n3. Using systemd (Linux):")
    print("   Create a service file for more robust automation")

def run_test():
    """Run the test suite"""
    print("\nRunning tests...")
    try:
        subprocess.check_call([sys.executable, 'test_monitor.py'])
        print("✓ Tests completed")
    except subprocess.CalledProcessError:
        print("✗ Some tests failed - check the output above")

def main():
    """Main setup function"""
    print("NYC Property Violation Monitor - Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    else:
        print(f"✓ Python {sys.version.split()[0]}")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup configuration
    if not setup_config():
        sys.exit(1)
    
    # Setup automation
    setup_cron()
    
    # Run tests
    run_test()
    
    print("\n" + "=" * 40)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Edit config.json to add your email password")
    print("2. Test with: python manual_run.py --no-email")
    print("3. Set up daily automation using one of the methods above")
    print("4. Monitor logs for any issues")

if __name__ == "__main__":
    main()
