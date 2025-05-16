# multiNYC - NYC Property Violation Monitor

A Python-based system that monitors NYC properties for new violations and sends daily email alerts.

## Features

- Monitor multiple NYC data sources:
  - 311 Service Requests
  - HPD (Housing Preservation & Development) Violations
  - OATH (Office of Administrative Trials & Hearings) Violations
  - DOB (Department of Buildings) Violations
- Daily email notifications for new violations
- Track violations by Block and Lot numbers
- Configurable email settings

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your settings in `config.json`

3. Run the monitor:
```bash
python violation_monitor.py
```

## Daily Automation

Set up a cron job to run daily:
```bash
# Add to crontab (crontab -e)
0 9 * * * /path/to/python /path/to/violation_monitor.py
```

## Configuration

See `config.json.example` for configuration options.
