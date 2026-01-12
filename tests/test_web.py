"""Tests for web Flask application."""
import pytest
import sys
import os
from datetime import datetime

# Add web directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import app, is_valid_url, check_if_js_time


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client


class TestRoutes:
    """Test Flask routes."""

    def test_index_route(self, client):
        """Test the index route loads."""
        response = client.get('/')
        assert response.status_code == 200

    def test_today_route(self, client):
        """Test the /today route."""
        response = client.get('/today')
        assert response.status_code == 200

    def test_aujourdhui_route(self, client):
        """Test the French /aujourd_hui route."""
        response = client.get('/aujourd_hui')
        assert response.status_code == 200

    def test_data_route(self, client):
        """Test the /data API endpoint."""
        response = client.get('/data')
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'  # Returns JSON as text
        # Check if response contains expected JSON fields
        data = response.get_data(as_text=True)
        assert 'day' in data
        assert 'month' in data
        assert 'year_arabic' in data

    def test_converter_route(self, client):
        """Test the date converter route."""
        response = client.get('/date_converter')
        assert response.status_code == 200

    def test_date_transformateur_route(self, client):
        """Test the French date converter route."""
        response = client.get('/date_transformateur')
        assert response.status_code == 200

    def test_gregorian_date_route(self, client):
        """Test converting a specific Gregorian date."""
        response = client.get('/gregorian_date/2024-01-01')
        assert response.status_code == 200

    def test_signup_route(self, client):
        """Test the webhook signup route."""
        response = client.get('/signup')
        assert response.status_code == 200

    def test_about_route(self, client):
        """Test the about page route."""
        response = client.get('/about')
        assert response.status_code == 200

    def test_au_sujet_de_route(self, client):
        """Test the French about route."""
        response = client.get('/au_sujet_de')
        assert response.status_code == 200

    def test_favicon_route(self, client):
        """Test the favicon route."""
        response = client.get('/favicon.ico')
        # May be 200 if file exists, or 404 if not
        assert response.status_code in [200, 404]

    def test_404_error(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent_route')
        assert response.status_code == 404


class TestUtilityFunctions:
    """Test utility functions in app.py."""

    def test_is_valid_url_valid(self):
        """Test is_valid_url with valid URLs."""
        assert is_valid_url('https://discord.com/api/webhooks/123/abc')
        assert is_valid_url('http://example.com/path')
        assert is_valid_url('https://test.com/')

    def test_is_valid_url_invalid(self):
        """Test is_valid_url with invalid URLs."""
        assert not is_valid_url('not a url')
        assert not is_valid_url('http://')
        assert not is_valid_url('://missing-scheme.com')
        assert not is_valid_url('')

    def test_check_if_js_time_same(self):
        """Test check_if_js_time when time matches server."""
        from freezegun import freeze_time
        # Freeze time to a specific moment
        fixed_time = datetime(2024, 1, 15, 12, 30, 45, 123456)

        with freeze_time(fixed_time):
            result = check_if_js_time(fixed_time)
            assert result == True

    def test_check_if_js_time_different(self):
        """Test check_if_js_time when time differs."""
        past = datetime(2020, 1, 1, 12, 0, 0)
        result = check_if_js_time(past)
        assert result == False


class TestLocalTimeSubmission:
    """Test local time submission flow."""

    def test_local_time_post(self, client):
        """Test submitting local time via POST."""
        response = client.post('/local_time', data={
            'local_time': str(int(datetime.now().timestamp())),
            'timezone_offset': '-480'  # PST offset
        })
        assert response.status_code == 200
        assert response.data == b'OK'


class TestDateConversion:
    """Test date conversion functionality."""

    def test_process_date_redirect(self, client):
        """Test that process_date redirects correctly."""
        response = client.post('/process_date', data={
            'date': '2024-01-01'
        }, follow_redirects=False)
        assert response.status_code == 302  # Redirect
        # Flask url_for can redirect to any of the route aliases
        assert '2024-01-01' in response.location
        assert any(route in response.location for route in
                   ['/gregorian_date/', '/vulgar_date/', '/date_grégorienne/', '/date_vulgaire/'])

    def test_linkable_converted_date_valid(self, client):
        """Test converting a valid date."""
        response = client.get('/gregorian_date/2024-06-15')
        assert response.status_code == 200

    def test_linkable_converted_date_invalid(self, client):
        """Test converting an invalid date format."""
        # Flask in test mode raises exceptions by default
        # We need to temporarily disable that to test error handling
        app.config['TESTING'] = False
        try:
            response = client.get('/gregorian_date/invalid-date')
            # Should return a 500 error for invalid date
            assert response.status_code == 500
        finally:
            app.config['TESTING'] = True
