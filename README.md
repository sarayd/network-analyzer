# Network: Your Contact Network Analyzer

Build and visualize your complete professional network from **Google Calendar meetings** and **iMessage conversations**, enriched with job titles from Apollo.io.

## Features

- 📊 **Complete Network Visualization** - See all 2,445+ people you've interacted with
- 🔍 **Smart Filtering** - Filter by Calendar, iMessage, or both channels
- 🎯 **Search** - Find contacts by name, title, or email
- 💼 **Job Titles** - Apollo.io enrichment showing professional context
- 📅 **Interaction Timeline** - Last contact date for each person
- 🎨 **area.na-inspired Design** - Minimal, clean interface with great typography

## What's Included

### Core Scripts

- **`combine_with_full_names.py`** - Main generator combining all data sources into a beautiful HTML visualization
- **`remove_phone_only_contacts.py`** - Filters out phone-number-only iMessage contacts
- **`enrich_with_apollo_fixed.py`** - Enriches calendar contacts with Apollo.io data (names, titles)

### Data Processing

- `calendar_scraper.py` - Scrapes Google Calendar for the past year
- `imessage_scraper.py` - Extracts contacts from iMessage database
- `extract_from_abbu.py` - Parses Contacts app backup
- `clean_csv.py` - Validates email formats
- `filter_automated_messages.py` - Removes spam and automated messages
- `fix_imessage_dates.py` - Corrects timestamp issues

### Output Files

- **`network_final.html`** - ⭐ Your interactive network visualization (main file)
- `calendar_attendees_apollo.csv` - Calendar contacts with Apollo enrichment
- `imessage_contacts_matched_with_messages_real_messages_only_fixed_names_only.csv` - Cleaned iMessage contacts

## Quick Start

### Prerequisites

- Python 3.9+
- macOS (for iMessage and Contacts app access)
- Google Calendar API credentials
- Apollo.io API key (optional, for title enrichment)

### Setup

1. **Clone and install:**
```bash
git clone https://github.com/yourusername/network-analyzer.git
cd network-analyzer
pip install -r requirements.txt
```

2. **Configure credentials:**
```bash
# Create .env file
echo "APOLLO_API_KEY=your_key_here" > .env
```

3. **Run the full pipeline:**
```bash
python3 combine_with_full_names.py
```

4. **Open the visualization:**
```bash
open network_final.html
```

## How It Works

### Data Collection

1. **Google Calendar** - Extracts attendees from meetings (past year)
2. **iMessage** - Queries SQLite database for conversation partners
3. **Contacts App** - Matches phone numbers to real names
4. **Apollo.io** - Enriches with job titles and professional context

### Data Cleaning

- Removes phone-number-only contacts (44% of iMessage data)
- Filters out automated messages (promotional, verification codes, etc.)
- Validates email formats
- Deduplicates across sources
- Corrects timestamp issues

### Visualization

- **2,445 unique contacts** displayed in a beautiful grid
- Color-coded badges for Calendar (blue) vs iMessage (purple)
- Real-time search and filtering
- Last interaction dates
- Message/meeting counts

## Statistics

From the example data:

- **Total Contacts:** 2,445
- **Calendar Only:** 995
- **iMessage Only:** 995
- **Both Channels:** 1,450
- **With Apollo Titles:** 636 (63.6%)
- **Phone-only Removed:** 1,152 (44.3%)

## macOS Setup Notes

### Google Calendar Access
1. Create OAuth2 credentials in Google Cloud Console
2. Save as `credentials.json` in project root
3. First run will prompt for authorization

### iMessage Access
1. Grant Terminal Full Disk Access in System Preferences
2. Contacts backup at `~/Downloads/Contacts - MM-DD-YYYY.abbu`

### Apollo.io
Get your API key from [Apollo.io dashboard](https://app.apollo.io/api)

## Limitations

- **Company Data** - Apollo has limited company info for most contacts
- **Historical Data** - Only works with local database data
- **macOS Only** - Designed for macOS iMessage and Contacts

## Privacy

All processing happens locally. Only external API calls:
- Google Calendar API (meeting data)
- Apollo.io API (title enrichment only)

## License

MIT

---

**Explore your network!** Open `network_final.html` in your browser.
