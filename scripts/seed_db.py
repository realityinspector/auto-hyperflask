#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def seed_database():
    from hyperflask.factory import create_app

    app = create_app()

    with app.app_context():
        from hyperflask.factory import db
        from app.models import User, TimelineEntry

        with db:
            print("Creating test users...")
            user1 = User.create(email="user1@test.com")
            user2 = User.create(email="user2@test.com")
            admin = User.create(email="admin@test.com")
            
            print(f"Created users: {user1.email}, {user2.email}, {admin.email}")
            
            print("\nCreating timeline entries...")
            users = [user1, user2, admin]
            now = datetime.utcnow()
            
            for i in range(20):
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                user = random.choice(users)
                
                entry = TimelineEntry.create(
                    user_id=user.id,
                    timestamp=timestamp,
                    status='approved',
                    caption=f"Timeline entry {i+1} from {user.email}",
                    photo_url=None
                )
                print(f"  Created entry {i+1}: {timestamp.strftime('%Y-%m-%d %H:%M')} by {user.email}")
            
            print(f"\n✓ Database seeded successfully!")
            print(f"  - 3 users created")
            print(f"  - 20 timeline entries created")
            print(f"\nTest user emails:")
            print(f"  - user1@test.com")
            print(f"  - user2@test.com")
            print(f"  - admin@test.com")


if __name__ == "__main__":
    seed_database()
