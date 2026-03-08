# MongoDB Quick Reference

## Starting MongoDB

**Windows (Service):**
```powershell
# MongoDB runs automatically as a service
# Verify it's running:
Get-Service MongoDB
```

**macOS:**
```bash
brew services start mongodb-community
brew services stop mongodb-community  # to stop
```

**Linux (Ubuntu/Debian):**
```bash
sudo systemctl start mongodb
sudo systemctl stop mongodb
sudo systemctl status mongodb
```

**Verify Connection:**
```bash
# Open MongoDB shell
mongo

# Or with pymongo (Python)
python -c "from pymongo import MongoClient; client = MongoClient(); print('Connected to:', client.address)"
```

## Common Operations

### Initialize Database
```bash
python scripts/init_db.py
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Database Tests Only
```bash
python -m pytest tests/test_database.py -v
```

### Query Collections via Python
```python
from src.database import get_collection

# Get collection
prices_col = get_collection("prices")

# Find latest price for AAPL
latest = prices_col.find_one(
    {"ticker": "AAPL"},
    sort=[("date", -1)]
)
print(latest)

# Count records
count = prices_col.count_documents({"ticker": "AAPL"})
print(f"Total AAPL records: {count}")

# Find price range
prices = list(prices_col.find(
    {
        "ticker": "AAPL",
        "date": {"$gte": "2023-01-01", "$lte": "2023-12-31"}
    }
).sort("date", 1))
```

### Using Database Operations
```python
from datetime import date
from src.db_operations import (
    upsert_price,
    get_prices,
    get_latest_price,
)

# Upsert price data
upsert_price("AAPL", date(2023, 1, 1), {
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.5,
    "volume": 1000000,
})

# Get latest price
latest = get_latest_price("AAPL")
print(latest)

# Get price range
prices = get_prices("AAPL", date(2023, 1, 1), date(2023, 12, 31))
print(f"Prices: {len(prices)}")
```

### Via MongoDB Shell
```javascript
// Connect to database
use stock_market

// Find latest AAPL price
db.prices.findOne({ticker: "AAPL"}, {sort: {date: -1}})

// Count records by ticker
db.prices.countDocuments({ticker: "AAPL"})

// Find price range
db.prices.find({
    ticker: "AAPL",
    date: {$gte: "2023-01-01", $lte: "2023-12-31"}
}).sort({date: 1})

// List all indexes
db.prices.getIndexes()

// Drop all documents (careful!)
db.prices.deleteMany({})
```

## Collection Names

| Collection | Purpose | Key Fields |
|---|---|---|
| `prices` | Daily OHLCV | `ticker`, `date` |
| `intraday` | 15-min data | `ticker`, `timestamp` |
| `news` | Headlines | `url`, `ticker` |
| `features_sentiment` | Daily sentiment | `ticker`, `date` |
| `predictions` | Model output | `ticker`, `date`, `model_name` |

## Troubleshooting

### MongoDB Connection Error
```
Error: ServerSelectionTimeoutError
Solution: Ensure MongoDB is running (systemctl start mongodb or service)
```

### No Collections Found
```
Solution: Run: python scripts/init_db.py
```

### Duplicate Key Error
```
Error: E11000 duplicate key error
Solution: This is prevented by unique indexes. Clear and reinitialize if needed:
python -c "from src.database import db; db.prices.delete_many({})"
```

### Tests Failing
```bash
# Check MongoDB is running
# Clear collections
python -c "from src.database import db, init_db; init_db()"
# Run tests
python -m pytest tests/ -v
```

## Environment Variables (Optional)

Add to `.env` if needed:
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=stock_market
```

Currently hardcoded in `src/database.py`:
```python
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "stock_market"
```

## Development Tips

### Clear All Data
```python
from src.database import db
collections = ["prices", "intraday", "news", "features_sentiment", "predictions"]
for col in collections:
    db[col].delete_many({})
print("All collections cleared")
```

### Recreate Indexes
```python
from src.database import init_db
init_db()  # Re-creates collections and indexes
```

### Backup Database
```bash
# Dump database to file
mongodump --db stock_market --out ./backup_$(date +%Y%m%d)

# Restore from backup
mongorestore --db stock_market ./backup_20230101
```

### Monitor Indexes
```python
from src.database import get_collection

for col_name in ["prices", "intraday", "news", "features_sentiment", "predictions"]:
    col = get_collection(col_name)
    indexes = col.list_indexes()
    print(f"\n{col_name} indexes:")
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['key']}")
```
