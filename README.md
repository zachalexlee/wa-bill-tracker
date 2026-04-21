# WA Bill Tracker - Site Structure

## Overview
Lobbyist-grade legislative intelligence site for Washington State bills.

## Architecture

### Frontend
- Single-page application (SPA) with vanilla JS
- Dark theme (lobbyist-friendly, long reading sessions)
- Mobile-responsive
- No external dependencies (self-contained)

### Data Pipeline
1. **Fetch** - Pull from WA Legislature API (app.leg.wa.gov)
2. **Parse** - Extract bill metadata, text, history
3. **Analyze** - AI-generated lobbyist analysis
4. **Store** - JSON files in /data/
5. **Serve** - Static HTML with dynamic loading

### File Structure
```
wa-bills/
├── index.html          # Main dashboard
├── bill.html           # Individual bill view
├── about.html          # Methodology, sources
├── css/
│   └── main.css        # Styles
├── js/
│   ├── app.js          # Main application
│   ├── api.js          # WA Legislature API wrapper
│   └── analysis.js     # Analysis rendering
├── data/
│   ├── bills.json      # Bill metadata
│   ├── analysis/       # Per-bill analysis files
│   └── stakeholders/   # Stakeholder database
└── archive/
    └── 2025-26/        # Session archives
```

### API Endpoints (WA Legislature)
- Bill search: `https://app.leg.wa.gov/billsummary/?year=2026&billnumber={n}`
- Bill text: `http://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/{type}%20Bills/{n}.pdf`
- Fiscal notes: `https://app.leg.wa.gov/billsummary/?year=2026&billnumber={n}&tab=fiscal`
- Committee materials: Linked from bill summary page

### Update Frequency
- New bills: Daily check at 6 AM
- Status changes: Every 4 hours
- Full analysis: Within 24 hours of significant amendment

### Features
- [ ] Bill search by keyword, sponsor, committee
- [ ] Filter by status, topic, business impact
- [ ] Email alerts for tracked bills
- [ ] RSS feed
- [ ] Export to PDF/Word
- [ ] Stakeholder position tracker
- [ ] Vote prediction model
- [ ] Amendment diff viewer

## Next Steps
1. Build API fetcher script
2. Create bill parser
3. Design analysis template
4. Set up auto-update cron job
5. Deploy to static hosting
