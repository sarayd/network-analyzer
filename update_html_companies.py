#!/usr/bin/env python3
"""Update network_final.html with company data from the enriched Apollo CSV.

Reads company data from calendar_attendees_apollo.csv and injects it into
the allContacts JavaScript array in network_final.html.
"""

import csv
import json
import re
import sys
from pathlib import Path

HTML_PATH = Path("network_final.html")
CSV_PATH = Path("calendar_attendees_apollo.csv")


def read_csv_with_comments(path):
    """Read CSV file, skipping comment lines."""
    data_lines = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#") and line.strip():
                data_lines.append(line)
    reader = csv.DictReader(data_lines)
    return list(reader)


def build_company_lookup(rows):
    """Build email -> company lookup from CSV rows."""
    lookup = {}
    for row in rows:
        email = row.get("email", "").strip().lower()
        company = row.get("company", "").strip()
        if email and company:
            lookup[email] = company
    return lookup


def main():
    if not HTML_PATH.exists():
        print(f"Error: {HTML_PATH} not found.")
        sys.exit(1)

    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        sys.exit(1)

    # Read company data from CSV
    rows = read_csv_with_comments(CSV_PATH)
    company_lookup = build_company_lookup(rows)
    print(f"Loaded {len(company_lookup)} contacts with company data from CSV.")

    # Read HTML
    html = HTML_PATH.read_text(encoding="utf-8")

    # Find the allContacts JSON array
    match = re.search(r"const allContacts = (\[.*?\]);", html, re.DOTALL)
    if not match:
        print("Error: Could not find allContacts array in HTML.")
        sys.exit(1)

    contacts = json.loads(match.group(1))
    print(f"Found {len(contacts)} contacts in HTML.")

    # Add company field to each contact
    enriched_count = 0
    for contact in contacts:
        handle = contact.get("handle", "").strip().lower()
        company = company_lookup.get(handle, "")
        contact["company"] = company if company else "\u2014"
        if company:
            enriched_count += 1

    print(f"Matched {enriched_count} contacts with company data.")

    # Replace the allContacts array in HTML
    new_json = json.dumps(contacts, ensure_ascii=False)
    new_html = html[:match.start()] + f"const allContacts = {new_json};" + html[match.end():]

    # Update the "With Company" stat if it exists
    new_html = re.sub(
        r'(<div class="stat-value" id="companyCount">)[^<]*(</div>)',
        rf"\g<1>{enriched_count}\g<2>",
        new_html,
    )

    HTML_PATH.write_text(new_html, encoding="utf-8")
    print(f"Updated {HTML_PATH} with company data.")
    print(f"  {enriched_count}/{len(contacts)} contacts have company info.")


if __name__ == "__main__":
    main()
