from hyperflask.factory import create_app
import pytest
import os
from datetime import datetime, timedelta
import random

# Import Playwright fixtures
pytest_plugins = ("pytest_playwright",)

# Import custom fixtures
from tests.fixtures.playwright_fixtures import (
    user_actions,
    admin_actions,
    timeline_actions,
    logged_in_user,
    logged_in_admin,
    setup_screenshots_dir,
)

# Import Stripe fixtures
from tests.fixtures.stripe_fixtures import (
    mock_stripe_api,
    stripe_service_mock,
    mock_stripe_customer,
    mock_stripe_subscription,
    mock_checkout_session,
    completed_checkout_session,
    stripe_webhook_event_checkout_completed,
    stripe_webhook_event_subscription_deleted,
    stripe_webhook_payload,
    stripe_plans,
)


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")


@pytest.fixture
def app():
    app = create_app(APP_ROOT)

    with app.app_context():
        # Seed test data
        from app.models import User, TimelineEntry
        from hyperflask.factory import db

        # Check if data already exists
        existing_users = list(User.find_all())
        if len(existing_users) == 0:
            # Create test users
            with db:
                user1 = User.create(email="user1@test.com")
                user2 = User.create(email="user2@test.com")
                admin = User.create(email="admin@test.com")

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

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide database session for tests"""
    from hyperflask.factory import db
    with app.app_context():
        yield db
