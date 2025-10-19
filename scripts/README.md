# Database Management Scripts

## reset_db.py

Clean and reset the database for development and testing.

### Usage

```bash
# Clear all data (will prompt for confirmation)
python3 scripts/reset_db.py

# Clear all data without confirmation
python3 scripts/reset_db.py --confirm

# Clear all data and reseed with test data
python3 scripts/reset_db.py --seed

# Clear and reseed without confirmation (useful for CI/CD)
python3 scripts/reset_db.py --seed --confirm
```

### What it does

- Deletes all users from the database
- Deletes all timeline entries from the database
- Optionally seeds with test data:
  - 3 test users (user1@test.com, user2@test.com, admin@test.com)
  - 20 timeline entries with random timestamps from the past 7 days
  - All entries set to 'approved' status

## seed_db.py

Seed the database with test data (without clearing existing data).

### Usage

```bash
python3 scripts/seed_db.py
```

## Environment-Specific Database Management

### Development (SQLite)
```bash
# Use dev config
cp config_dev.yml config.yml

# Reset dev database
python3 scripts/reset_db.py --seed --confirm
```

### Production (PostgreSQL)
```bash
# Use prod config
cp config_prod.yml config.yml

# Reset prod database (BE CAREFUL!)
python3 scripts/reset_db.py --seed
```

### Testing
```bash
# Reset database for E2E tests
python3 scripts/reset_db.py --seed --confirm

# Run tests
python3 -m pytest tests/
```
