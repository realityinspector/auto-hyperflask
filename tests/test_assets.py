import pytest
import os


def test_assets_built():
    """Test that all assets are built"""
    # Check JavaScript bundle
    assert os.path.exists('public/dist/main.js'), "JavaScript bundle not found"
    assert os.path.getsize('public/dist/main.js') > 0, "JavaScript bundle is empty"

    # Check CSS bundle
    assert os.path.exists('public/dist/main.css'), "CSS bundle not found"
    assert os.path.getsize('public/dist/main.css') > 0, "CSS bundle is empty"

    # Check Bootstrap Icons
    assert os.path.exists('public/bootstrap-icons/bootstrap-icons.css'), "Bootstrap Icons CSS not found"


def test_javascript_bundle_contains_libraries():
    """Test that JavaScript bundle includes our dependencies"""
    with open('public/dist/main.js', 'r') as f:
        content = f.read()

    # Check for Alpine.js
    assert 'Alpine' in content, "Alpine.js not found in bundle"

    # Check for HTMX (htmx might be minified to different names)
    assert 'htmx' in content or 'hx-' in content, "HTMX not found in bundle"


def test_css_bundle_contains_tailwind():
    """Test that CSS bundle includes Tailwind classes"""
    with open('public/dist/main.css', 'r') as f:
        content = f.read()

    # Check for common Tailwind utilities
    assert any(x in content for x in ['.flex', '.grid', '.hidden']), "Tailwind utilities not found in CSS"


def test_assets_served_by_app(client):
    """Test that assets are accessible via the app"""
    # Test JavaScript
    response = client.get('/static/dist/main.js')
    assert response.status_code == 200, "JavaScript asset not served"
    assert response.content_length > 0, "JavaScript asset is empty"

    # Test CSS
    response = client.get('/static/dist/main.css')
    assert response.status_code == 200, "CSS asset not served"
    assert response.content_length > 0, "CSS asset is empty"

    # Test Bootstrap Icons
    response = client.get('/static/bootstrap-icons/bootstrap-icons.css')
    assert response.status_code == 200, "Bootstrap Icons not served"


def test_homepage_includes_assets(client):
    """Test that homepage includes compiled assets"""
    response = client.get('/')
    assert response.status_code == 200

    html = response.data.decode('utf-8')

    # Check for JavaScript
    assert 'dist/main.js' in html, "JavaScript not included in homepage"

    # Check for CSS
    assert 'dist/main.css' in html, "CSS not included in homepage"

    # Check for Bootstrap Icons
    assert 'bootstrap-icons' in html, "Bootstrap Icons not included in homepage"


def test_alpine_js_initialization(client):
    """Test that Alpine.js initialization code is present"""
    response = client.get('/static/dist/main.js')
    assert response.status_code == 200

    content = response.data.decode('utf-8')
    assert 'Alpine' in content, "Alpine.js code not found"


def test_htmx_loaded(client):
    """Test that HTMX is included in the bundle"""
    response = client.get('/static/dist/main.js')
    assert response.status_code == 200

    content = response.data.decode('utf-8')
    # HTMX might be minified, check for common patterns
    assert 'htmx' in content.lower() or 'hx-' in content, "HTMX not found in bundle"
