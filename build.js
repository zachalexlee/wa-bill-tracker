const fs = require('fs');
const path = require('path');

// Read all bill data files
const dataDir = path.join(__dirname, 'data');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

let allBills = [];
files.forEach(file => {
    const data = JSON.parse(fs.readFileSync(path.join(dataDir, file)));
    allBills = allBills.concat(data);
});

// Generate bill cards HTML
function generateBillCards() {
    return allBills.map(bill => {
        const billNum = bill.number || 'Unknown';
        const title = bill.title || 'Title not available';
        const status = bill.status || 'Unknown';
        const sponsors = bill.sponsors ? bill.sponsors.join(', ') : 'No sponsors listed';
        
        // Determine status class
        let statusClass = 'status-pending';
        if (status.includes('Pass') || status.includes('Signed')) statusClass = 'status-active';
        if (status.includes('Dead') || status.includes('Failed')) statusClass = 'status-dead';
        
        return `
            <div class="bill-card">
                <div class="bill-header">
                    <div>
                        <div class="bill-number">${billNum}</div>
                        <span class="bill-type">${billNum.startsWith('HB') ? 'House Bill' : 'Senate Bill'}</span>
                    </div>
                    <span class="status-badge ${statusClass}">${status}</span>
                </div>
                <div class="bill-body">
                    <h2 class="bill-title">${title}</h2>
                    <div class="meta-grid">
                        <div class="meta-item">
                            <div class="meta-label">Sponsors</div>
                            <div class="meta-value">${sponsors}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Status</div>
                            <div class="meta-value">${status}</div>
                        </div>
                    </div>
                    <button class="expand-btn" onclick="alert('Full analysis coming soon for ${billNum}')">
                        📋 View Analysis
                    </button>
                </div>
            </div>
        `;
    }).join('\n');
}

// Read template
let html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');

// Replace the single demo bill with all bills
const billCards = generateBillCards();
const billGridRegex = /<div class="bill-grid">[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/;
html = html.replace(/<div class="bill-grid">[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/, `<div class="bill-grid">\n${billCards}\n</div>`);

// Write updated HTML
fs.writeFileSync(path.join(__dirname, 'dist', 'index.html'), html);
console.log(`Built site with ${allBills.length} bills`);
