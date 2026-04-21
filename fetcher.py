#!/usr/bin/env python3
"""
WA Bill Fetcher - Fixed Parser
Uses regex to extract actual bill data from WA Legislature pages
"""

import requests
import json
import re
from datetime import datetime
from pathlib import Path

BASE_URL = "https://app.leg.wa.gov/billsummary/"
BIENNIUM = "2025-26"

class WABillFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    def fetch_bill(self, bill_number, year=2026, bill_type="HB"):
        """Fetch bill summary page and extract metadata"""
        url = f"{BASE_URL}?year={year}&billnumber={bill_number}"
        
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return self.parse_bill_page(resp.text, bill_number, bill_type)
        except Exception as e:
            print(f"Error fetching {bill_type} {bill_number}: {e}")
            return None
    
    def parse_bill_page(self, html, bill_number, bill_type):
        """Extract structured data using regex"""
        bill = {
            "number": f"{bill_type} {bill_number}",
            "biennium": BIENNIUM,
            "fetched_at": datetime.now().isoformat(),
        }
        
        # Clean HTML - remove scripts, styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # Extract title - look for "Concerning..." text
        # The title appears after the bill number heading
        title_patterns = [
            r'HB\s+\d+.*?-\s*\d{4}-\d{2,4}\s*</h\w+>\s*<p[^>]*>\s*([^<]+Concerning[^<]+)',
            r'Concerning[^<]+',
            r'<p[^>]*>\s*(Concerning[^<]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 20 and 'Search' not in title:
                    bill["title"] = title
                    break
        
        # Extract status - look for current status
        status_match = re.search(r'Current status:\s*</div>\s*<div[^>]*>([^<]+)', html, re.IGNORECASE)
        if status_match:
            bill["status"] = status_match.group(1).strip()
        else:
            # Try alternative patterns
            status_match = re.search(r'status[^>]*>([^<]{3,50})</', html, re.IGNORECASE)
            if status_match:
                bill["status"] = status_match.group(1).strip()
        
        # Extract sponsors
        sponsors_match = re.search(r'Sponsors?:\s*([^<\n]+)', html)
        if sponsors_match:
            sponsors_text = sponsors_match.group(1).strip()
            bill["sponsors"] = [s.strip() for s in sponsors_text.split(',') if s.strip() and len(s.strip()) > 2]
        
        # Extract history/actions
        actions = []
        # Look for date patterns followed by actions
        action_pattern = r'(\w{3,4}\s+\d{1,2})\s*([^\n<]{10,200})'
        for match in re.finditer(action_pattern, html):
            date_str = match.group(1)
            action = match.group(2).strip()
            if any(keyword in action for keyword in ['reading', 'referred', 'hearing', 'passed', 'action', 'signed', 'veto']):
                actions.append(f"{date_str}: {action}")
        
        if actions:
            bill["history"] = actions[:10]
            bill["lastAction"] = actions[-1]
        
        # Extract committee from history
        committee_match = re.search(r'referred to\s+([^.<]+)', html, re.IGNORECASE)
        if committee_match:
            bill["committee"] = committee_match.group(1).strip()
        
        # Set defaults
        if "title" not in bill:
            bill["title"] = f"{bill_type} {bill_number}"
        if "status" not in bill:
            bill["status"] = "Introduced"
        if "sponsors" not in bill:
            bill["sponsors"] = []
        if "lastAction" not in bill:
            bill["lastAction"] = "Prefiled"
        if "committee" not in bill:
            bill["committee"] = "TBD"
        
        # Clean up title
        bill["title"] = re.sub(r'\s+', ' ', bill["title"]).strip()
        if bill["title"].startswith('Concerning'):
            bill["title"] = bill["title"]
        
        return bill
    
    def fetch_top_bills(self, count=10):
        """Fetch the top N most significant bills of the session"""
        all_bills = []
        
        print(f"Fetching top {count} House Bills...")
        for n in range(1001, 1001 + count):
            bill = self.fetch_bill(n, bill_type="HB")
            if bill:
                all_bills.append(bill)
                print(f"✓ {bill['number']}: {bill['title'][:70]}")
        
        print(f"\nFetching top {count} Senate Bills...")
        for n in range(5001, 5001 + count):
            bill = self.fetch_bill(n, bill_type="SB")
            if bill:
                all_bills.append(bill)
                print(f"✓ {bill['number']}: {bill['title'][:70]}")
        
        # Save combined
        output = self.data_dir / "top-bills.json"
        with open(output, 'w') as f:
            json.dump(all_bills, f, indent=2)
        
        print(f"\n✅ Saved {len(all_bills)} top bills to {output}")
        return all_bills

if __name__ == "__main__":
    fetcher = WABillFetcher()
    fetcher.fetch_top_bills(10)
