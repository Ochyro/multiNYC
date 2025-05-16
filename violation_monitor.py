#!/usr/bin/env python3
"""
NYC Property Violation Monitor
Monitors NYC Open Data for new violations at a specific property
and sends daily email alerts.
"""

import json
import requests
import smtplib
import sqlite3
import os
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NYCDataFetcher:
    """Handles fetching data from NYC Open Data APIs"""
    
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.base_url = "https://data.cityofnewyork.us/resource"
        
        # NYC Open Data dataset IDs
        self.datasets = {
            '311_complaints': '311-service-requests',  # erm2-nwe9.json
            'hpd_violations': 'hpd-violations',  # wvxf-dwi5.json
            'oath_violations': 'oath-violations',  # 6bgk-3dad.json
            'dob_violations': 'dob-violations'  # 3h2n-5cm9.json
        }
        
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> List[Dict]:
        """Make API request to NYC Open Data"""
        url = f"{self.base_url}/{endpoint}.json"
        
        if self.api_token:
            params['$$app_token'] = self.api_token
            
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return []
    
    def get_311_complaints(self, block: str, lot: str, since_date: str) -> List[Dict]:
        """Fetch 311 complaints for a property"""
        params = {
            '$where': f"incident_address LIKE '%{block} %{lot}%' AND created_date > '{since_date}'",
            '$order': 'created_date DESC',
            '$limit': 1000
        }
        return self._make_request('erm2-nwe9', params)
    
    def get_hpd_violations(self, block: str, lot: str, since_date: str) -> List[Dict]:
        """Fetch HPD violations for a property"""
        params = {
            '$where': f"block = '{block}' AND lot = '{lot}' AND inspectiondate > '{since_date}'",
            '$order': 'inspectiondate DESC',
            '$limit': 1000
        }
        return self._make_request('wvxf-dwi5', params)
    
    def get_oath_violations(self, block: str, lot: str, since_date: str) -> List[Dict]:
        """Fetch OATH violations for a property"""
        params = {
            '$where': f"block = '{block}' AND lot = '{lot}' AND hearing_date > '{since_date}'",
            '$order': 'hearing_date DESC',
            '$limit': 1000
        }
        return self._make_request('6bgk-3dad', params)
    
    def get_dob_violations(self, block: str, lot: str, since_date: str) -> List[Dict]:
        """Fetch DOB violations for a property"""
        params = {
            '$where': f"block = '{block}' AND lot = '{lot}' AND issue_date > '{since_date}'",
            '$order': 'issue_date DESC',
            '$limit': 1000
        }
        return self._make_request('3h2n-5cm9', params)

class ViolationTracker:
    """Handles tracking violations to identify new ones"""
    
    def __init__(self):
        self.db_path = 'violations.db'
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for tracking violations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                violation_id TEXT NOT NULL,
                block TEXT NOT NULL,
                lot TEXT NOT NULL,
                violation_date TEXT NOT NULL,
                created_date TEXT NOT NULL,
                UNIQUE(source, violation_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_new_violation(self, source: str, violation_id: str) -> bool:
        """Check if a violation is new"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT 1 FROM violations WHERE source = ? AND violation_id = ?',
            (source, violation_id)
        )
        
        result = cursor.fetchone() is None
        conn.close()
        return result
    
    def track_violation(self, source: str, violation_id: str, block: str, 
                       lot: str, violation_date: str):
        """Track a new violation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO violations 
            (source, violation_id, block, lot, violation_date, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source, violation_id, block, lot, violation_date, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

class EmailNotifier:
    """Handles sending email notifications"""
    
    def __init__(self, config: Dict):
        self.smtp_server = config['smtp_server']
        self.smtp_port = config['smtp_port']
        self.from_email = config['from_email']
        self.from_password = config['from_password']
        self.to_emails = config['to_emails']
    
    def send_violation_report(self, violations: Dict[str, List], block: str, lot: str):
        """Send email with violation report"""
        if not any(violations.values()):
            logger.info("No new violations to report")
            return
        
        msg = MimeMultipart()
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)
        msg['Subject'] = f"NYC Property Violations - Block {block}, Lot {lot}"
        
        # Create email body
        body = self._create_email_body(violations, block, lot)
        msg.attach(MimeText(body, 'html'))
        
        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.from_email, self.from_password)
            
            for to_email in self.to_emails:
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            server.quit()
            logger.info(f"Report sent to {len(self.to_emails)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def _create_email_body(self, violations: Dict[str, List], block: str, lot: str) -> str:
        """Create HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                table {{border-collapse: collapse; width: 100%;}}
                th, td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
                th {{background-color: #f2f2f2;}}
                .section {{margin-bottom: 20px;}}
                .no-violations {{color: #666; font-style: italic;}}
            </style>
        </head>
        <body>
            <h2>NYC Property Violations Report</h2>
            <p><strong>Property:</strong> Block {block}, Lot {lot}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
        """
        
        for source, viol_list in violations.items():
            if viol_list:
                html += f"<div class='section'><h3>{source.replace('_', ' ').title()}</h3>"
                html += "<table><tr>"
                
                # Add headers based on violation type
                if source == '311_complaints':
                    html += "<th>Date</th><th>Type</th><th>Description</th><th>Address</th></tr>"
                    for viol in viol_list:
                        html += f"<tr><td>{viol.get('created_date', '')}</td>"
                        html += f"<td>{viol.get('complaint_type', '')}</td>"
                        html += f"<td>{viol.get('descriptor', '')}</td>"
                        html += f"<td>{viol.get('incident_address', '')}</td></tr>"
                elif source == 'hpd_violations':
                    html += "<th>Date</th><th>Type</th><th>Description</th><th>Class</th></tr>"
                    for viol in viol_list:
                        html += f"<tr><td>{viol.get('inspectiondate', '')}</td>"
                        html += f"<td>{viol.get('violationtype', '')}</td>"
                        html += f"<td>{viol.get('violationdescription', '')}</td>"
                        html += f"<td>{viol.get('class', '')}</td></tr>"
                elif source == 'oath_violations':
                    html += "<th>Hearing Date</th><th>Violation</th><th>Status</th></tr>"
                    for viol in viol_list:
                        html += f"<tr><td>{viol.get('hearing_date', '')}</td>"
                        html += f"<td>{viol.get('violation_type', '')}</td>"
                        html += f"<td>{viol.get('status', '')}</td></tr>"
                elif source == 'dob_violations':
                    html += "<th>Issue Date</th><th>Type</th><th>Description</th><th>Severity</th></tr>"
                    for viol in viol_list:
                        html += f"<tr><td>{viol.get('issue_date', '')}</td>"
                        html += f"<td>{viol.get('violation_type_code', '')}</td>"
                        html += f"<td>{viol.get('description', '')}</td>"
                        html += f"<td>{viol.get('severity', '')}</td></tr>"
                
                html += "</table></div>"
            else:
                html += f"<div class='section'><h3>{source.replace('_', ' ').title()}</h3>"
                html += "<p class='no-violations'>No new violations found</p></div>"
        
        html += "</body></html>"
        return html

class ViolationMonitor:
    """Main class that orchestrates the violation monitoring"""
    
    def __init__(self, config_path: str = 'config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.data_fetcher = NYCDataFetcher(
            self.config.get('nyc_data', {}).get('api_tokens', {}).get('socrata_token')
        )
        self.tracker = ViolationTracker()
        self.notifier = EmailNotifier(self.config['email'])
        
        self.block = self.config['property']['block']
        self.lot = self.config['property']['lot']
    
    def check_violations(self):
        """Check for new violations and send email if found"""
        logger.info(f"Checking violations for Block {self.block}, Lot {self.lot}")
        
        # Get yesterday's date as starting point
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        new_violations = {
            '311_complaints': [],
            'hpd_violations': [],
            'oath_violations': [],
            'dob_violations': []
        }
        
        # Check 311 complaints
        complaints = self.data_fetcher.get_311_complaints(self.block, self.lot, yesterday)
        for complaint in complaints:
            complaint_id = complaint.get('unique_key')
            if complaint_id and self.tracker.is_new_violation('311_complaints', complaint_id):
                new_violations['311_complaints'].append(complaint)
                self.tracker.track_violation(
                    '311_complaints', complaint_id, self.block, self.lot,
                    complaint.get('created_date')
                )
        
        # Check HPD violations
        hpd_violations = self.data_fetcher.get_hpd_violations(self.block, self.lot, yesterday)
        for violation in hpd_violations:
            violation_id = violation.get('violationid')
            if violation_id and self.tracker.is_new_violation('hpd_violations', violation_id):
                new_violations['hpd_violations'].append(violation)
                self.tracker.track_violation(
                    'hpd_violations', violation_id, self.block, self.lot,
                    violation.get('inspectiondate')
                )
        
        # Check OATH violations
        oath_violations = self.data_fetcher.get_oath_violations(self.block, self.lot, yesterday)
        for violation in oath_violations:
            violation_id = violation.get('summons_number')
            if violation_id and self.tracker.is_new_violation('oath_violations', violation_id):
                new_violations['oath_violations'].append(violation)
                self.tracker.track_violation(
                    'oath_violations', violation_id, self.block, self.lot,
                    violation.get('hearing_date')
                )
        
        # Check DOB violations
        dob_violations = self.data_fetcher.get_dob_violations(self.block, self.lot, yesterday)
        for violation in dob_violations:
            violation_id = violation.get('isn_dob_bis_viol')
            if violation_id and self.tracker.is_new_violation('dob_violations', violation_id):
                new_violations['dob_violations'].append(violation)
                self.tracker.track_violation(
                    'dob_violations', violation_id, self.block, self.lot,
                    violation.get('issue_date')
                )
        
        # Log results
        total_new = sum(len(viol_list) for viol_list in new_violations.values())
        logger.info(f"Found {total_new} new violations")
        
        # Send email notification
        self.notifier.send_violation_report(new_violations, self.block, self.lot)

def main():
    """Main function"""
    try:
        monitor = ViolationMonitor()
        monitor.check_violations()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
