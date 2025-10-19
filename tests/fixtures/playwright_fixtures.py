"""
Playwright fixtures for E2E testing
Provides reusable fixtures for user and admin testing
"""

import pytest
from playwright.sync_api import Page, expect
from typing import Generator


class UserActions:
    """Reusable user actions for testing"""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def goto_home(self):
        """Navigate to homepage"""
        self.page.goto(f"{self.base_url}/")
        expect(self.page).to_have_title("AutoHyperFlask")

    def goto_timeline(self):
        """Navigate to timeline page"""
        self.page.goto(f"{self.base_url}/timeline")

    def goto_admin(self):
        """Navigate to admin page"""
        self.page.goto(f"{self.base_url}/admin")

    def click_nav_link(self, text: str):
        """Click a navigation link by text"""
        self.page.get_by_role("link", name=text).click()

    def login(self, email: str, password: str = "password"):
        """Login as a user"""
        # Navigate to login page if it exists
        self.page.goto(f"{self.base_url}/auth/login")
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="password"]', password)
        self.page.click('button[type="submit"]')

    def logout(self):
        """Logout current user"""
        self.page.get_by_role("link", name="Logout").click()

    def wait_for_page_load(self):
        """Wait for page to fully load"""
        self.page.wait_for_load_state("networkidle")

    def take_screenshot(self, name: str):
        """Take a screenshot for debugging"""
        self.page.screenshot(path=f"tests/screenshots/{name}.png")

    def assert_on_page(self, path: str):
        """Assert that we're on a specific page"""
        expect(self.page).to_have_url(f"{self.base_url}{path}")

    def assert_text_visible(self, text: str):
        """Assert that text is visible on the page"""
        expect(self.page.get_by_text(text)).to_be_visible()

    def assert_heading_visible(self, text: str):
        """Assert that a heading with text is visible"""
        expect(self.page.get_by_role("heading", name=text)).to_be_visible()


class AdminActions(UserActions):
    """Admin-specific actions extending UserActions"""

    def login_as_admin(self):
        """Login as admin user"""
        self.login("admin@test.com")

    def view_dashboard_stats(self):
        """View and return dashboard statistics"""
        stats = {}
        stats['total_users'] = self.page.locator('.stat-value').nth(0).text_content()
        stats['total_entries'] = self.page.locator('.stat-value').nth(1).text_content()
        stats['approved'] = self.page.locator('.stat-value').nth(2).text_content()
        return stats

    def get_timeline_entries_count(self):
        """Count timeline entries in admin table"""
        return self.page.locator('table tbody tr').count()

    def approve_entry(self, entry_id: int):
        """Approve a timeline entry"""
        # This would depend on your admin UI implementation
        pass

    def delete_entry(self, entry_id: int):
        """Delete a timeline entry"""
        # This would depend on your admin UI implementation
        pass


class TimelineActions(UserActions):
    """Timeline-specific actions"""

    def get_visible_entries_count(self):
        """Count visible timeline entries"""
        return self.page.locator('.card').count()

    def get_entry_by_index(self, index: int):
        """Get timeline entry by index"""
        return self.page.locator('.card').nth(index)

    def assert_entry_has_timestamp(self, index: int):
        """Assert that entry has a timestamp"""
        entry = self.get_entry_by_index(index)
        expect(entry.locator('.card-title')).to_be_visible()

    def assert_entry_has_status(self, index: int, status: str):
        """Assert that entry has a specific status"""
        entry = self.get_entry_by_index(index)
        expect(entry.get_by_text(status)).to_be_visible()


@pytest.fixture
def user_actions(page: Page, live_server) -> Generator[UserActions, None, None]:
    """Fixture providing user actions"""
    actions = UserActions(page, live_server.url())
    yield actions


@pytest.fixture
def admin_actions(page: Page, live_server) -> Generator[AdminActions, None, None]:
    """Fixture providing admin actions"""
    actions = AdminActions(page, live_server.url())
    yield actions


@pytest.fixture
def timeline_actions(page: Page, live_server) -> Generator[TimelineActions, None, None]:
    """Fixture providing timeline actions"""
    actions = TimelineActions(page, live_server.url())
    yield actions


@pytest.fixture
def logged_in_user(user_actions: UserActions) -> UserActions:
    """Fixture that logs in a regular user"""
    user_actions.login("user1@test.com")
    user_actions.wait_for_page_load()
    return user_actions


@pytest.fixture
def logged_in_admin(admin_actions: AdminActions) -> AdminActions:
    """Fixture that logs in an admin user"""
    admin_actions.login_as_admin()
    admin_actions.wait_for_page_load()
    return admin_actions


@pytest.fixture(autouse=True)
def setup_screenshots_dir():
    """Ensure screenshots directory exists"""
    import os
    os.makedirs("tests/screenshots", exist_ok=True)
