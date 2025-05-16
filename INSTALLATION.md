# NYC Property Violation Monitor - Installation Guide

This guide will help you set up the NYC Property Violation Monitor to automatically track violations for your property and receive daily email alerts.

## Prerequisites

- Python 3.7 or higher
- Internet connection
- Email account (Gmail recommended)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ochyro/multiNYC.git
   cd multiNYC
   ```

2. **Run the setup script:**
   ```bash
   python setup.py
   ```
   
   This will:
   - Install required dependencies
   - Create configuration file
   - Guide you through initial setup
   - Run tests to verify everything works

3. **Configure your email password:**
   Edit `config.json` and add your email password or app password

4. **Test the system:**
   ```bash
   python manual_run.py --no-email
   ```

5. **Set up daily automation** (choose one):
   - **Cron (Linux/Mac):** Add to crontab: `0 9 * * * cd /path/to/multiNYC && python violation_monitor.py`
   - **Scheduler script:** Run `python scheduler.py` and keep it running
   - **Windows Task Scheduler:** Create a task to run `violation_monitor.py` daily

## Manual Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy the configuration template:
```bash
cp config.json.example config.json
```

Edit `config.json` with your settings:

```json
{
  "property": {
    "block": "YOUR_BLOCK_NUMBER",
    "lot": "YOUR_LOT_NUMBER"
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "your_email@gmail.com",
    "from_password": "your_app_password",
    "to_emails": ["recipient@email.com"]
  }
}
```

### 3. Find Your Block and Lot Numbers

You can find your block and lot numbers:
- From property tax bills
- NYC Department of Finance website
- Using [ACRIS](https://a836-acris.nyc.gov/DS/DocumentSearch/BBL) with your address

### 4. Email Setup

#### For Gmail:
1. Enable 2-factor authentication
2. Create an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `config.json`

#### For other email providers:
- Update `smtp_server` and `smtp_port` accordingly
- Some providers: Yahoo (`smtp.mail.yahoo.com:587`), Outlook (`smtp-mail.outlook.com:587`)

## Testing

Run the test suite:
```bash
python test_monitor.py
```

Test with your property (without sending email):
```bash
python manual_run.py --no-email
```

Test full run with email:
```bash
python manual_run.py
```

## Daily Automation Options

### Option 1: Cron (Linux/Mac)

Add to your crontab (`crontab -e`):
```bash
0 9 * * * cd /path/to/multiNYC && /usr/bin/python3 violation_monitor.py
```

### Option 2: Python Scheduler

Run the scheduler script:
```bash
python scheduler.py
```

Keep this running in the background (you may want to use `screen` or `tmux`).

### Option 3: Systemd Service (Linux)

Create `/etc/systemd/system/nyc-violations.service`:
```ini
[Unit]
Description=NYC Property Violation Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/multiNYC
ExecStart=/usr/bin/python3 violation_monitor.py
Restart=daily

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nyc-violations.service
sudo systemctl start nyc-violations.service
```

### Option 4: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Daily" at your preferred time
4. Set action to start `python.exe` with arguments `violation_monitor.py`
5. Set start in directory to your multiNYC folder

## Troubleshooting

### No violations found
- Verify block and lot numbers are correct
- Check if there have been any recent violations
- Test with a property known to have violations

### Email not sending
- Verify email credentials
- Check firewall/antivirus blocking SMTP
- For Gmail, ensure app password is used, not regular password
- Test with: `python manual_run.py --verbose`

### API errors
- NYC Open Data APIs can be slow or temporarily unavailable
- The system will retry and log errors
- Check logs for specific error messages

### Permission errors
- Ensure Python has permission to create files in the directory
- Database file (`violations.db`) needs write permissions

## Data Sources

The monitor checks these NYC Open Data sources:
- **311 Service Requests:** Complaints from residents
- **HPD Violations:** Housing preservation violations  
- **OATH Violations:** Administrative violations and hearings
- **DOB Violations:** Department of Buildings violations

## Files Created

- `violations.db`: SQLite database tracking known violations
- `config.json`: Your configuration (keep secure, contains email password)
- Log files (if configured)

## Security Notes

- `config.json` contains your email password - keep it secure
- Use app passwords instead of regular email passwords
- Consider encrypting the config file for production deployments
- Review email recipients periodically

## Advanced Configuration

### Custom API Tokens

You can register for Socrata API tokens to avoid rate limiting:
```json
{
  "nyc_data": {
    "api_tokens": {
      "socrata_token": "your_token_here"
    }
  }
}
```

### Schedule Configuration

Modify the schedule in `scheduler.py`:
```python
schedule.every().day.at("09:00").do(run_violation_check)
```

Change `"09:00"` to your preferred time.

## Support

For issues:
1. Check this documentation
2. Run `python test_monitor.py` to diagnose problems
3. Check logs for error messages
4. Verify your configuration matches the examples

## Limitations

- Only tracks violations for one property at a time
- Relies on NYC Open Data availability
- Email alerts require internet connection
- Historical violations won't trigger new alerts

---

Need help? Create an issue on GitHub with your error messages and configuration (remove sensitive information).
