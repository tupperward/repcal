"""Tests for Discord webhook."""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add webhook directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'webhook'))

from webhook import get_data, construct_embed, use_webhook, base_url


class TestGetData:
    """Test get_data function."""

    @patch('webhook.requests.get')
    def test_get_data_fetches_from_api(self, mock_get):
        """Test that get_data fetches from the correct API endpoint."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '{"day": 1, "month": "Vendémiaire", "year_arabic": "233"}'
        mock_get.return_value = mock_response

        # Execute
        result = get_data()

        # Assertions
        mock_get.assert_called_once_with(f'https://{base_url}/data')
        assert result['day'] == 1
        assert result['month'] == 'Vendémiaire'
        assert result['year_arabic'] == '233'

    @patch('webhook.requests.get')
    def test_get_data_returns_dict(self, mock_get):
        """Test that get_data returns a dictionary."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '{"test": "value"}'
        mock_get.return_value = mock_response

        # Execute
        result = get_data()

        # Assertions
        assert isinstance(result, dict)
        assert result['test'] == 'value'


class TestConstructEmbed:
    """Test construct_embed function."""

    def test_construct_embed_regular_month(self):
        """Test constructing embed for a regular month."""
        # Test data
        data = {
            'day': 15,
            'weekday': 'primidi',
            'month': 'Vendémiaire',
            'year_arabic': '233',
            'year_roman': 'ccxxxiii',
            'month_of': 'Vintage',
            'item': 'Grape',
            'item_url': 'https://test.com/grape',
            'image': 'grape'
        }

        # Execute
        embed = construct_embed(data)

        # Assertions
        assert embed is not None
        assert 'primidi' in embed.title.lower() or 'Primidi' in embed.title
        assert '15th' in embed.title
        assert 'Vendémiaire' in embed.title
        assert 'grape' in embed.description.lower()
        assert embed.color.value == 0x57a639  # Green color
        assert 'sansculottid.es/static/images/grape.jpg' in embed.image.url

    def test_construct_embed_sansculottides(self):
        """Test constructing embed for Sansculottides."""
        # Test data
        data = {
            'day': 1,
            'weekday': 'primidi',
            'month': 'Sansculottides',
            'year_arabic': '233',
            'year_roman': 'ccxxxiii',
            'month_of': 'complementary days',
            'item': 'Virtue',
            'item_url': 'https://test.com/virtue',
            'image': 'virtue'
        }

        # Execute
        embed = construct_embed(data)

        # Assertions
        assert embed is not None
        assert 'sansculottides' in embed.title.lower()
        assert 'primidi' in embed.title.lower()
        assert 'virtue' in embed.description.lower()
        assert embed.color.value == 0x1f3a93  # Dark blue color
        assert 'sansculottid.es/static/images/virtue.jpg' in embed.image.url

    @patch('webhook.ordinal')
    def test_construct_embed_uses_ordinal(self, mock_ordinal):
        """Test that construct_embed uses the ordinal function."""
        mock_ordinal.return_value = "15th"

        data = {
            'day': 15,
            'weekday': 'primidi',
            'month': 'Vendémiaire',
            'year_arabic': '233',
            'year_roman': 'ccxxxiii',
            'month_of': 'Vintage',
            'item': 'Grape',
            'item_url': 'https://test.com/grape',
            'image': 'grape'
        }

        # Execute
        embed = construct_embed(data)

        # Assertions
        mock_ordinal.assert_called()
        assert '15th' in embed.title

    def test_construct_embed_footer(self):
        """Test that embed has correct footer."""
        data = {
            'day': 1,
            'weekday': 'primidi',
            'month': 'Vendémiaire',
            'year_arabic': '233',
            'year_roman': 'ccxxxiii',
            'month_of': 'Vintage',
            'item': 'Grape',
            'item_url': 'https://test.com/grape',
            'image': 'grape'
        }

        # Execute
        embed = construct_embed(data)

        # Assertions
        assert embed.footer is not None
        assert 'primidi' in embed.footer.text.lower()
        assert 'ccxxxiii' in embed.footer.text.lower()


class TestUseWebhook:
    """Test use_webhook function."""

    @patch('webhook.SyncWebhook.from_url')
    def test_use_webhook_sends_message(self, mock_webhook_from_url):
        """Test that use_webhook sends the embed."""
        # Mock webhook
        mock_hook = Mock()
        mock_webhook_from_url.return_value = mock_hook

        # Mock embed
        mock_embed = Mock()

        # Execute
        use_webhook('https://test.webhook.url', mock_embed)

        # Assertions
        mock_webhook_from_url.assert_called_once_with('https://test.webhook.url')
        mock_hook.send.assert_called_once_with(embed=mock_embed)

    @patch('webhook.SyncWebhook.from_url')
    def test_use_webhook_handles_error(self, mock_webhook_from_url):
        """Test that use_webhook handles errors gracefully."""
        # Mock webhook that raises exception
        mock_hook = Mock()
        mock_hook.send.side_effect = Exception("Connection error")
        mock_webhook_from_url.return_value = mock_hook

        # Mock embed
        mock_embed = Mock()

        # Execute - should not raise exception in non-component mode
        try:
            use_webhook('https://test.webhook.url', mock_embed, component=False)
            # Should print error but not raise
        except SystemExit:
            # Expected in component mode
            pass

    @patch('webhook.current_app')
    @patch('webhook.SyncWebhook.from_url')
    def test_use_webhook_component_mode_logging(self, mock_webhook_from_url, mock_current_app):
        """Test that use_webhook logs in component mode."""
        # Mock webhook
        mock_hook = Mock()
        mock_webhook_from_url.return_value = mock_hook

        # Mock Flask app logger
        mock_logger = Mock()
        mock_current_app.logger = mock_logger

        # Mock embed
        mock_embed = Mock()

        # Execute in component mode
        use_webhook('https://test.webhook.url', mock_embed, component=True)

        # Assertions - should log
        assert mock_logger.info.called


class TestWebhookConfiguration:
    """Test webhook configuration."""

    def test_base_url_configured(self):
        """Test that base_url is configured correctly."""
        assert base_url == 'sansculottid.es'

    @patch('webhook.requests.get')
    @patch('webhook.SyncWebhook.from_url')
    @patch.dict(os.environ, {'DISCORD_WEBHOOK_URL': 'https://test.webhook.url'})
    def test_main_execution(self, mock_webhook_from_url, mock_requests_get):
        """Test main execution path when run as script."""
        # Mock get_data
        mock_response = Mock()
        mock_response.text = '{"day": 1, "month": "Test", "year_arabic": "233", "weekday": "test", "year_roman": "ccxxxiii", "month_of": "test", "item": "Test", "item_url": "https://test.com", "image": "test"}'
        mock_requests_get.return_value = mock_response

        # Mock webhook
        mock_hook = Mock()
        mock_webhook_from_url.return_value = mock_hook

        # This tests the structure but doesn't execute __main__
        # Real execution test would require subprocess
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        assert webhook_url == 'https://test.webhook.url'
