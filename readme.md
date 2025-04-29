# Manufacturing Contact Scraper

A Python scraper to collect contact information for manufacturing executives in South Africa.

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Run the scraper:
```bash
python main.py
```

## Features

- Rotates through multiple API keys and CSE IDs to avoid quota limits
- Extracts contact information using regex patterns
- Saves results in both CSV and JSON formats
- Includes logging and error handling
- Cleans and standardizes contact information

## Output

Results are saved in the `output` directory with timestamps:
- CSV file: `manufacturing_contacts_YYYYMMDD_HHMMSS.csv`
- JSON file: `manufacturing_contacts_YYYYMMDD_HHMMSS.json`

Logs are saved in the `logs` directory.