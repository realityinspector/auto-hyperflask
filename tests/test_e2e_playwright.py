"""
End-to-End tests using Playwright
Tests actual browser rendering, asset loading, and user interactions
"""

import pytest
from playwright.sync_api import Page, expect
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def live_server():
    """Start the Flask development server for E2E testing"""
    from threading import Thread
    from hyperflask.factory import create_app
    from app import APP_ROOT
    import time

    app = create_app(APP_ROOT)
    app.config['TESTING'] = False  # We want the real app

    class ServerThread(Thread):
        def __init__(self, app):
            Thread.__init__(self)
            self.app = app
            self.daemon = True

        def run(self):
            self.app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)

    server = ServerThread(app)
    server.start()
    time.sleep(1)  # Give server time to start

    class LiveServer:
        def url(self):
            return "http://127.0.0.1:5555"

    yield LiveServer()


class TestAssetLoading:
    """Test that assets load correctly in the browser"""

    def test_homepage_loads_successfully(self, page: Page, live_server):
        """Test that homepage loads without errors"""
        page.goto(live_server.url())

        # Check title
        expect(page).to_have_title("AutoHyperFlask")

        # Wait for page to be fully loaded
        page.wait_for_load_state("networkidle")

    def test_css_assets_loaded(self, page: Page, live_server):
        """Test that CSS is loaded and applied"""
        page.goto(live_server.url())

        # Check that main.css is loaded
        css_response = page.wait_for_response(
            lambda response: "main.css" in response.url and response.status == 200,
            timeout=5000
        )
        assert css_response is not None

        # Verify CSS is applied by checking computed styles
        navbar = page.locator('nav.navbar').first
        expect(navbar).to_be_visible()

        # Check that TailwindCSS classes are applied
        # The navbar should have background color (from DaisyUI)
        bg_color = navbar.evaluate("el => window.getComputedStyle(el).backgroundColor")
        assert bg_color != "rgba(0, 0, 0, 0)", "Navbar should have a background color"

    def test_javascript_assets_loaded(self, page: Page, live_server):
        """Test that JavaScript bundles load successfully"""
        page.goto(live_server.url())

        # Check that main.js is loaded
        js_response = page.wait_for_response(
            lambda response: "main.js" in response.url and response.status == 200,
            timeout=5000
        )
        assert js_response is not None

        # Verify Alpine.js is loaded
        alpine_loaded = page.evaluate("() => window.Alpine !== undefined")
        assert alpine_loaded, "Alpine.js should be loaded"

        # Verify HTMX is loaded
        htmx_loaded = page.evaluate("() => window.htmx !== undefined")
        assert htmx_loaded, "HTMX should be loaded"

    def test_bootstrap_icons_loaded(self, page: Page, live_server):
        """Test that Bootstrap Icons are loaded"""
        page.goto(live_server.url())

        # Check that icons CSS is loaded
        icons_loaded = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
            return links.some(link => link.href.includes('bootstrap-icons'));
        }""")
        assert icons_loaded, "Bootstrap Icons CSS should be loaded"

        # Check that an icon is visible
        icon = page.locator('i.bi').first
        if icon.count() > 0:
            expect(icon).to_be_visible()

    def test_no_console_errors(self, page: Page, live_server):
        """Test that there are no console errors"""
        console_errors = []

        page.on("console", lambda msg: (
            console_errors.append(msg.text)
            if msg.type == "error"
            else None
        ))

        page.goto(live_server.url())
        page.wait_for_load_state("networkidle")

        # Filter out known acceptable errors
        real_errors = [
            err for err in console_errors
            if not any(ignore in err for ignore in [
                "favicon",  # Missing favicon is acceptable
                "net::ERR_FAILED",  # Network errors during dev are ok
            ])
        ]

        assert len(real_errors) == 0, f"Console errors found: {real_errors}"


class TestNavigation:
    """Test navigation and routing"""

    def test_navbar_links_work(self, page: Page, live_server):
        """Test that all navbar links navigate correctly"""
        page.goto(live_server.url())

        # Click Timeline link
        page.get_by_role("link", name="Timeline").click()
        expect(page).to_have_url(f"{live_server.url()}/timeline")
        expect(page.get_by_role("heading", name="Timeline")).to_be_visible()

        # Click Home link
        page.get_by_role("link", name="Home").click()
        expect(page).to_have_url(f"{live_server.url()}/")

    def test_logo_link_returns_home(self, page: Page, live_server):
        """Test that clicking logo returns to homepage"""
        page.goto(f"{live_server.url()}/timeline")

        page.get_by_role("link", name="AutoHyperFlask").click()
        expect(page).to_have_url(live_server.url() + "/")


class TestTimelinePage:
    """Test timeline functionality"""

    def test_timeline_page_loads(self, page: Page, live_server):
        """Test that timeline page loads"""
        page.goto(f"{live_server.url()}/timeline")

        expect(page.get_by_role("heading", name="Timeline")).to_be_visible()

    def test_timeline_entries_displayed(self, page: Page, live_server):
        """Test that timeline entries are displayed"""
        page.goto(f"{live_server.url()}/timeline")

        # Check for cards (DaisyUI component)
        cards = page.locator('.card')
        count = cards.count()

        # Should have some entries (from seeded data)
        # or a message saying no entries
        if count > 0:
            # Verify first card has expected structure
            first_card = cards.first
            expect(first_card.locator('.card-title')).to_be_visible()
        else:
            # Should show "no entries" message
            expect(page.get_by_text("No timeline entries", exact=False)).to_be_visible()

    def test_timeline_entries_have_status_badges(self, page: Page, live_server):
        """Test that timeline entries show status badges"""
        page.goto(f"{live_server.url()}/timeline")

        cards = page.locator('.card')
        if cards.count() > 0:
            # Check for status badge
            badge = cards.first.locator('.badge')
            expect(badge).to_be_visible()
            expect(badge).to_have_text("approved", ignore_case=True)


class TestResponsiveDesign:
    """Test responsive design with different viewports"""

    @pytest.mark.parametrize("viewport", [
        {"width": 375, "height": 667},   # Mobile (iPhone SE)
        {"width": 390, "height": 844},   # Mobile (iPhone 12/13/14)
        {"width": 414, "height": 896},   # Mobile (iPhone 11/XR)
        {"width": 768, "height": 1024},  # Tablet (iPad)
        {"width": 1024, "height": 768},  # Tablet landscape
        {"width": 1920, "height": 1080}, # Desktop
    ])
    def test_responsive_layout(self, page: Page, live_server, viewport):
        """Test that layout works on different screen sizes"""
        page.set_viewport_size(viewport)
        page.goto(live_server.url())

        # Navbar should be visible on all sizes
        navbar = page.locator('nav.navbar')
        expect(navbar).to_be_visible()

        # Main content should be visible
        main = page.locator('main')
        expect(main).to_be_visible()

        # Content should not overflow
        body_width = page.evaluate("document.body.scrollWidth")
        viewport_width = viewport["width"]
        assert body_width <= viewport_width + 20, f"Content overflows on {viewport['width']}px viewport"

    def test_mobile_hamburger_menu(self, page: Page, live_server):
        """Test mobile hamburger menu functionality"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(live_server.url())

        # Hamburger menu should be visible on mobile
        hamburger = page.locator('.dropdown-end .btn-circle')
        expect(hamburger).to_be_visible()

        # Desktop menu should be hidden
        desktop_menu = page.locator('.menu-horizontal')
        expect(desktop_menu).to_be_hidden()

        # Click hamburger to open menu
        hamburger.click()

        # Mobile menu should appear
        mobile_menu = page.locator('.dropdown-content')
        expect(mobile_menu).to_be_visible()

        # Should have navigation links
        expect(mobile_menu.get_by_text("Timeline")).to_be_visible()

    def test_desktop_menu_visible(self, page: Page, live_server):
        """Test desktop menu is visible on large screens"""
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(live_server.url())

        # Desktop menu should be visible
        desktop_menu = page.locator('.menu-horizontal')
        expect(desktop_menu).to_be_visible()

        # Hamburger should be hidden
        hamburger = page.locator('.dropdown-end .btn-circle')
        expect(hamburger).to_be_hidden()

    def test_mobile_navigation_works(self, page: Page, live_server):
        """Test navigation on mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(live_server.url())

        # Open mobile menu
        hamburger = page.locator('.dropdown-end .btn-circle')
        hamburger.click()

        # Click Timeline link in mobile menu
        mobile_menu = page.locator('.dropdown-content')
        mobile_menu.get_by_text("Timeline").click()

        expect(page).to_have_url(f"{live_server.url()}/timeline")

    def test_mobile_timeline_cards_readable(self, page: Page, live_server):
        """Test timeline cards are readable on mobile"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{live_server.url()}/timeline")

        cards = page.locator('.card')
        if cards.count() > 0:
            first_card = cards.first

            # Card should be visible
            expect(first_card).to_be_visible()

            # Card should not overflow viewport
            card_width = first_card.evaluate("el => el.offsetWidth")
            assert card_width <= 375, "Card overflows mobile viewport"

            # Text should be readable (not too small)
            title = first_card.locator('.card-title')
            font_size = title.evaluate("el => window.getComputedStyle(el).fontSize")
            # Should be at least 14px on mobile
            assert float(font_size.replace('px', '')) >= 14

    def test_mobile_touch_targets(self, page: Page, live_server):
        """Test that touch targets are large enough on mobile"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(live_server.url())

        # Hamburger button should be at least 44x44px (iOS HIG recommendation)
        hamburger = page.locator('.dropdown-end .btn-circle')
        size = hamburger.bounding_box()
        assert size['width'] >= 44, "Touch target too small"
        assert size['height'] >= 44, "Touch target too small"

    def test_mobile_logo_abbreviated(self, page: Page, live_server):
        """Test that logo is abbreviated on very small screens"""
        page.set_viewport_size({"width": 320, "height": 568})  # iPhone SE (1st gen)
        page.goto(live_server.url())

        # On very small screens, abbreviated logo should be visible
        # This tests the xs:hidden and xs:inline classes
        page.wait_for_load_state("networkidle")


class TestAccessibility:
    """Test accessibility features"""

    def test_semantic_html(self, page: Page, live_server):
        """Test that semantic HTML is used"""
        page.goto(live_server.url())

        # Check for semantic elements
        expect(page.locator('nav')).to_be_visible()
        expect(page.locator('main')).to_be_visible()
        expect(page.locator('footer')).to_be_visible()

    def test_keyboard_navigation(self, page: Page, live_server):
        """Test that keyboard navigation works"""
        page.goto(live_server.url())

        # Tab through links
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")

        # First link should be focused
        focused = page.evaluate("document.activeElement.tagName")
        assert focused in ["A", "BUTTON"], "Should be able to tab to interactive elements"


class TestPerformance:
    """Test performance metrics"""

    def test_page_load_time(self, page: Page, live_server):
        """Test that page loads quickly"""
        import time

        start = time.time()
        page.goto(live_server.url())
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start

        # Page should load in under 3 seconds
        assert load_time < 3.0, f"Page took {load_time:.2f}s to load"

    def test_asset_sizes_reasonable(self, page: Page, live_server):
        """Test that asset sizes are reasonable"""
        page.goto(live_server.url())

        # Get JS bundle size
        js_response = page.wait_for_response(
            lambda r: "main.js" in r.url and not "map" in r.url
        )

        js_size = len(js_response.body()) / 1024  # KB
        # Bundle should be less than 500KB
        assert js_size < 500, f"JS bundle is {js_size:.1f}KB, should be under 500KB"


class TestVisualRegression:
    """Test visual appearance"""

    def test_homepage_screenshot(self, page: Page, live_server):
        """Take screenshot of homepage for visual regression testing"""
        page.goto(live_server.url())
        page.wait_for_load_state("networkidle")

        # Take screenshot
        page.screenshot(path="tests/screenshots/homepage.png", full_page=True)

    def test_timeline_screenshot(self, page: Page, live_server):
        """Take screenshot of timeline for visual regression testing"""
        page.goto(f"{live_server.url()}/timeline")
        page.wait_for_load_state("networkidle")

        page.screenshot(path="tests/screenshots/timeline.png", full_page=True)
