#!/usr/bin/env python3
"""Enrich calendar contacts CSV with company data from Apollo.io People Enrichment API."""

import csv
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

CSV_PATH = Path("calendar_attendees_apollo.csv")
APOLLO_API_URL = "https://api.apollo.io/v1/people/match"
RATE_LIMIT_DELAY = 0.5  # seconds between requests to respect rate limits


def get_api_key():
    """Load Apollo API key from .env file or environment variable."""
    api_key = os.environ.get("APOLLO_API_KEY")
    if api_key:
        return api_key

    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("APOLLO_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")

    return None


def enrich_contact(email, api_key):
    """Call Apollo People Enrichment API to get company for an email."""
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }
    payload = {
        "api_key": api_key,
        "email": email,
    }

    try:
        resp = requests.post(APOLLO_API_URL, json=payload, headers=headers, timeout=10)
        if resp.status_code == 429:
            print("  Rate limited, waiting 60s...")
            time.sleep(60)
            resp = requests.post(APOLLO_API_URL, json=payload, headers=headers, timeout=10)

        if resp.status_code != 200:
            return None

        data = resp.json()
        person = data.get("person")
        if not person:
            return None

        org = person.get("organization") or {}
        return {
            "company": org.get("name", ""),
        }
    except requests.RequestException as e:
        print(f"  Request failed for {email}: {e}")
        return None


def read_csv_with_comments(path):
    """Read CSV file, preserving comment lines at the top."""
    comments = []
    data_lines = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                comments.append(line)
            elif line.strip():
                data_lines.append(line)

    reader = csv.DictReader(data_lines)
    rows = list(reader)
    return comments, reader.fieldnames, rows


def write_csv_with_comments(path, comments, fieldnames, rows):
    """Write CSV file with comment lines at the top."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        for comment in comments:
            f.write(comment)
        f.write("\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    api_key = get_api_key()
    if not api_key:
        print("Error: No Apollo API key found.")
        print("Set APOLLO_API_KEY in .env file or as an environment variable.")
        print('  echo "APOLLO_API_KEY=your_key_here" > .env')
        sys.exit(1)

    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        sys.exit(1)

    comments, fieldnames, rows = read_csv_with_comments(CSV_PATH)

    if "company" not in fieldnames:
        print("Error: 'company' column not found in CSV.")
        sys.exit(1)

    # Count contacts that already have company data
    already_enriched = sum(1 for r in rows if r.get("company", "").strip())
    need_enrichment = [i for i, r in enumerate(rows) if r.get("email", "").strip() and not r.get("company", "").strip()]

    print(f"Total contacts: {len(rows)}")
    print(f"Already have company: {already_enriched}")
    print(f"Need enrichment: {len(need_enrichment)}")
    print()

    if not need_enrichment:
        print("All contacts already have company data.")
        return

    enriched_count = 0
    failed_count = 0

    for idx, row_idx in enumerate(need_enrichment):
        row = rows[row_idx]
        email = row["email"].strip()
        name = row.get("full_name", row.get("name", "")).strip()

        print(f"[{idx + 1}/{len(need_enrichment)}] Enriching {name} ({email})...", end=" ")

        result = enrich_contact(email, api_key)

        if result and result["company"]:
            rows[row_idx]["company"] = result["company"]
            enriched_count += 1
            print(f"-> {result['company']}")
        else:
            failed_count += 1
            print("-> no company found")

        time.sleep(RATE_LIMIT_DELAY)

        # Save progress every 50 contacts
        if (idx + 1) % 50 == 0:
            total_with_company = sum(1 for r in rows if r.get("company", "").strip())
            updated_comments = []
            for c in comments:
                if c.startswith("# With company:"):
                    updated_comments.append(f"# With company: {total_with_company}\n")
                else:
                    updated_comments.append(c)
            write_csv_with_comments(CSV_PATH, updated_comments, fieldnames, rows)
            print(f"  [Saved progress: {total_with_company} with company]")

    # Final save
    total_with_company = sum(1 for r in rows if r.get("company", "").strip())
    updated_comments = []
    for c in comments:
        if c.startswith("# With company:"):
            updated_comments.append(f"# With company: {total_with_company}\n")
        else:
            updated_comments.append(c)
    write_csv_with_comments(CSV_PATH, updated_comments, fieldnames, rows)

    print()
    print(f"Done! Enriched {enriched_count} contacts with company data.")
    print(f"Failed/no data: {failed_count}")
    print(f"Total with company: {total_with_company}/{len(rows)}")


if __name__ == "__main__":
    main()
