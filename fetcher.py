#!/usr/bin/env python3
"""
WA Bill Fetcher
Pulls bill data from Washington State Legislature API
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
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    def fetch_bill(self, bill_number, year=2026):
        """Fetch bill summary page and extract metadata"""
        url = f"{BASE_URL}?year={year}&billnumber={bill_number}"
        
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return self.parse_bill_page(resp.text, bill_number)
        except Exception as e:
            print(f"Error fetching HB {bill_number}: {e}")
            return None
    
    def parse_bill_page(self, html, bill_number):
        """Extract structured data from bill summary HTML"""
        # Basic parsing - in production use BeautifulSoup
        bill = {
            "number": f"HB {bill_number}",
            "biennium": BIENNIUM,
            "fetched_at": datetime.now().isoformat(),
            "raw_html": html[:5000]  # Truncated for storage
        }
        
        # Extract title
        title_match = re.search(r'Concerning (.+?)\.', html)
        if title_match:
            bill["title"] = f"Concerning {title_match.group(1)}."
        
        # Extract status
        status_match = re.search(r'Current status:</div>\s*<div[^>]*>([^<]+)', html)
        if status_match:
            bill["status"] = status_match.group(1).strip()
        
        # Extract sponsors
        sponsors_match = re.search(r'Sponsors:([^<]+)', html)
        if sponsors_match:
            bill["sponsors"] = [s.strip() for s in sponsors_match.group(1).split(',')]
        
        return bill
    
    def fetch_range(self, start=1001, end=1100, bill_type="HB"):
        """Fetch a range of bills"""
        bills = []
        for n in range(start, end + 1):
            bill = self.fetch_bill(n, bill_type)
            if bill:
                bills.append(bill)
                print(f"✓ Fetched {bill_type} {n}")
        
        # Save to JSON
        output = self.data_dir / f"bills_{bill_type}_{start}_{end}.json"
        with open(output, 'w') as f:
            json.dump(bills, f, indent=2)
        
        print(f"Saved {len(bills)} bills to {output}")
        return bills
    
    def fetch_all_types(self):
        """Fetch House and Senate bills - extended range"""
        all_bills = []
        # House Bills 1001-1200
        all_bills.extend(self.fetch_range(1001, 1200, "HB"))
        # Senate Bills 5001-5200
        all_bills.extend(self.fetch_range(5001, 5200, "SB"))
        return all_bills
    
    def get_bill_text_url(self, bill_number, bill_type="House"):
        """Generate URL for bill PDF"""
        return (
            f"http://lawfilesext.leg.wa.gov/biennium/{BIENNIUM}/"
            f"Pdf/Bills/{bill_type}%20Bills/{bill_number}.pdf"
        )

if __name__ == "__main__":
    fetcher = WABillFetcher()
    # Fetch both House and Senate bills
    fetcher.fetch_all_types()
