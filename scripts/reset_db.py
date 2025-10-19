#!/usr/bin/env python3
"""
Database reset script for development and testing.
Clears all data and optionally reseeds with test data.

Usage:
    python scripts/reset_db.py              # Clear all data
    python scripts/reset_db.py --seed       # Clear and reseed with test data
    python scripts/reset_db.py --confirm    # Skip confirmation prompt
"""
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def reset_database(seed=False, confirm=True):
    from hyperflask.factory import create_app, db

    app = create_app()

    if confirm:
        response = input("⚠️  This will DELETE ALL DATA from the database. Continue? [y/N]: ")
        if response.lower() != 'y':
            print("❌ Reset cancelled")
            return

    with app.app_context():
        from app.models import User, TimelineEntry

        print("🗑️  Deleting all data...")

        # Delete all timeline entries
        entries_deleted = 0
        for entry in TimelineEntry.find_all():
            entry.delete()
            entries_deleted += 1

        # Delete all users
        users_deleted = 0
        for user in User.find_all():
            user.delete()
            users_deleted += 1

        print(f"✓ Deleted {users_deleted} users")
        print(f"✓ Deleted {entries_deleted} timeline entries")

        if seed:
            print("\n🌱 Seeding test data...")

            # Create test users
            user1 = User.create(email="user1@test.com")
            user2 = User.create(email="user2@test.com")
            admin = User.create(email="admin@test.com")

            print(f"✓ Created users: {user1.email}, {user2.email}, {admin.email}")

            # Create timeline entries
            users = [user1, user2, admin]
            now = datetime.utcnow()

            for i in range(20):
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)

                timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                user = random.choice(users)

                TimelineEntry.create(
                    user_id=user.id,
                    timestamp=timestamp,
                    status='approved',
                    caption=f"Timeline entry {i+1} from {user.email}",
                    photo_url=None
                )

            print(f"✓ Created 20 timeline entries")
            print(f"\n✅ Database reset and seeded successfully!")
        else:
            print(f"\n✅ Database reset successfully!")
            print("💡 Run with --seed flag to add test data")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reset database for dev/test")
    parser.add_argument("--seed", action="store_true", help="Seed with test data after reset")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    reset_database(seed=args.seed, confirm=not args.confirm)
