const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

let allBills = [];
files.forEach(file => {
    try {
        const data = JSON.parse(fs.readFileSync(path.join(dataDir, file)));
        allBills = allBills.concat(data);
    } catch (e) {
        console.log(`Skipping ${file}: ${e.message}`);
    }
});

// Remove duplicates by bill number
const seen = new Set();
allBills = allBills.filter(bill => {
    const key = bill.number || bill.bill_number || '';
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
});

// Save merged data
const outputFile = path.join(dataDir, 'all-bills.json');
fs.writeFileSync(outputFile, JSON.stringify(allBills, null, 2));
console.log(`Merged ${allBills.length} unique bills to ${outputFile}`);

// Copy to dist
const distDir = path.join(__dirname, 'dist');
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Copy index.html
fs.copyFileSync(
    path.join(__dirname, 'index.html'),
    path.join(distDir, 'index.html')
);

// Copy data
const distDataDir = path.join(distDir, 'data');
if (!fs.existsSync(distDataDir)) {
    fs.mkdirSync(distDataDir, { recursive: true });
}
fs.copyFileSync(outputFile, path.join(distDataDir, 'all-bills.json'));

console.log('Build complete. Files ready in dist/');
