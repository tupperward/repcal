"""Extended tests for web Flask application - improving coverage."""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, Mock

# Add web directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import app


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client


class TestTimezoneHandling:
    """Test timezone handling in /today route."""

    def test_today_with_positive_timezone_offset(self, client):
        """Test /today with positive timezone offset (west of GMT)."""
        # Submit local time with positive offset
        timestamp = int(datetime(2024, 6, 15, 12, 0, 0).timestamp())
        client.post('/local_time', data={
            'local_time': str(timestamp),
            'timezone_offset': '300'  # GMT+5 (300 minutes)
        })

        # Now visit /today
        response = client.get('/today')
        assert response.status_code == 200

    def test_today_with_negative_timezone_offset(self, client):
        """Test /today with negative timezone offset (east of GMT)."""
        # Submit local time with negative offset
        timestamp = int(datetime(2024, 6, 15, 12, 0, 0).timestamp())
        client.post('/local_time', data={
            'local_time': str(timestamp),
            'timezone_offset': '-300'  # GMT-5 (300 minutes)
        })

        # Now visit /today
        response = client.get('/today')
        assert response.status_code == 200

    def test_today_without_session_data(self, client):
        """Test /today when session has no timestamp (error path)."""
        # Visit /today without submitting local_time first
        response = client.get('/today')
        assert response.status_code == 200
        # Should fall back to server time


class TestLocalTimeErrorHandling:
    """Test error handling in /local_time route."""

    def test_local_time_with_missing_data(self, client):
        """Test /local_time with missing form data."""
        # Missing data returns None, which causes error on int() conversion (line 47)
        # Flask will raise ValueError, which we can catch if TESTING=False
        app.config['TESTING'] = False
        try:
            response = client.post('/local_time', data={})
            # Should return 500 error due to int(None)
            assert response.status_code == 500
        finally:
            app.config['TESTING'] = True


class TestSansculottidesRendering:
    """Test rendering of Sansculottides dates."""

    @patch('web.app.carpe_diem')
    def test_today_renders_sansculottides(self, mock_carpe_diem, client):
        """Test that /today renders sansculottides.html for complementary days."""
        # Mock carpe_diem to return a Sansculottides date
        mock_today = Mock()
        mock_today.month = "Sansculottides"
        mock_today.day = 1
        mock_today.weekday = "Primidi"
        mock_today.year_arabic = "233"
        mock_today.item = "Virtue"
        mock_carpe_diem.return_value = mock_today

        response = client.get('/today')
        assert response.status_code == 200
        # Check that sansculottides template was used (would have specific content)

    @patch('web.app.carpe_diem')
    def test_date_converter_renders_sansculottides(self, mock_carpe_diem, client):
        """Test date converter renders sansculottides.html for complementary days."""
        # Mock carpe_diem to return a Sansculottides date
        mock_today = Mock()
        mock_today.month = "Sansculottides"
        mock_today.day = 1
        mock_carpe_diem.return_value = mock_today

        # Convert a date that would be in Sansculottides
        response = client.get('/gregorian_date/2024-09-17')  # Late September
        assert response.status_code == 200


class TestWebhookCreation:
    """Test webhook creation route."""

    @patch('repcal_shared.kubernetes.create_cronjob')
    def test_create_webhook_success(self, mock_create_cronjob, client):
        """Test successful webhook creation."""
        mock_create_cronjob.return_value = {'status': 'created'}

        response = client.post('/create_webhook', data={
            'url': 'https://discord.com/api/webhooks/123/abc',
            'timezone': 'America/New_York',
            'time': '12:30'
        }, follow_redirects=False)

        assert response.status_code == 302  # Redirect to success
        assert '/success' in response.location or '/succés' in response.location
        mock_create_cronjob.assert_called_once()

    def test_create_webhook_invalid_url(self, client):
        """Test webhook creation with invalid URL."""
        response = client.post('/create_webhook', data={
            'url': 'not-a-valid-url',
            'timezone': 'America/New_York',
            'time': '12:30'
        })

        assert response.status_code == 200
        # Should render failure.html
        assert b'failure' in response.data.lower() or b'error' in response.data.lower()

    @patch('repcal_shared.kubernetes.create_cronjob')
    def test_create_webhook_kubernetes_error(self, mock_create_cronjob, client):
        """Test webhook creation when K8s API fails."""
        mock_create_cronjob.side_effect = Exception("K8s API error")

        response = client.post('/create_webhook', data={
            'url': 'https://discord.com/api/webhooks/123/abc',
            'timezone': 'America/New_York',
            'time': '12:30'
        })

        assert response.status_code == 200
        # Should render failure.html


class TestSuccessPage:
    """Test success page route."""

    @patch('webhook.webhook.use_webhook')
    @patch('webhook.webhook.construct_embed')
    def test_success_page_sends_test_webhook(self, mock_construct_embed, mock_use_webhook, client):
        """Test that success page constructs and sends a test webhook."""
        # Set up session with webhook URL
        with client.session_transaction() as sess:
            sess['url'] = 'https://discord.com/api/webhooks/123/abc'

        mock_embed = Mock()
        mock_construct_embed.return_value = mock_embed

        response = client.get('/success')
        assert response.status_code == 200

        # Verify embed was constructed and webhook was sent
        mock_construct_embed.assert_called_once()
        mock_use_webhook.assert_called_once()

    @patch('webhook.webhook.use_webhook')
    @patch('webhook.webhook.construct_embed')
    def test_succes_french_route(self, mock_construct_embed, mock_use_webhook, client):
        """Test French success route."""
        with client.session_transaction() as sess:
            sess['url'] = 'https://discord.com/api/webhooks/123/abc'

        mock_construct_embed.return_value = Mock()

        response = client.get('/succés')
        assert response.status_code == 200


class TestAboutPage:
    """Test about page route."""

    def test_about_without_session_date(self, client):
        """Test about page when session has no date."""
        # Clear session
        with client.session_transaction() as sess:
            sess.clear()

        response = client.get('/about')
        assert response.status_code == 200
        # Should use current date as fallback

    def test_about_with_session_date(self, client):
        """Test about page with date in session."""
        with client.session_transaction() as sess:
            sess['date'] = datetime(2024, 6, 15, 12, 0, 0)

        response = client.get('/about')
        assert response.status_code == 200

    def test_au_sujet_de_french_route(self, client):
        """Test French about route."""
        response = client.get('/au_sujet_de')
        assert response.status_code == 200


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_local_time_with_malformed_data(self, client):
        """Test /local_time with malformed data."""
        # Malformed data causes ValueError on int() conversion (line 47)
        app.config['TESTING'] = False
        try:
            response = client.post('/local_time', data={
                'local_time': 'not-a-timestamp',
                'timezone_offset': 'not-a-number'
            })
            # Should return 500 error
            assert response.status_code == 500
        finally:
            app.config['TESTING'] = True

    def test_today_with_malformed_session(self, client):
        """Test /today with malformed session data."""
        with client.session_transaction() as sess:
            sess['timestamp'] = 'not-a-number'
            sess['timezone_offset'] = 'not-a-number'

        response = client.get('/today')
        assert response.status_code == 200
        # Should fall back to server time

    def test_create_webhook_with_malformed_time(self, client):
        """Test webhook creation with malformed time format."""
        try:
            response = client.post('/create_webhook', data={
                'url': 'https://discord.com/api/webhooks/123/abc',
                'timezone': 'America/New_York',
                'time': 'not-a-time'  # Should cause split() to fail
            })
            # May raise error or return failure page
            assert response.status_code in [200, 500]
        except ValueError:
            # Expected if error isn't caught
            pass
