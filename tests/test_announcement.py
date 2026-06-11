import pytest
from unittest.mock import patch, MagicMock, mock_open
from discord import Embed

import announcement


def make_mock_cronjob(webhook_url=None, extra_env=None):
    envs = []
    if webhook_url:
        ev = MagicMock()
        ev.name = 'DISCORD_WEBHOOK_URL'
        ev.value = webhook_url
        envs.append(ev)
    for name, value in (extra_env or {}).items():
        ev = MagicMock()
        ev.name = name
        ev.value = value
        envs.append(ev)
    container = MagicMock()
    container.env = envs
    cj = MagicMock()
    cj.spec.job_template.spec.template.spec.containers = [container]
    return cj


class TestGetNamespace:
    def test_reads_from_sa_file(self):
        with patch('builtins.open', mock_open(read_data='my-namespace\n')):
            assert announcement.get_namespace() == 'my-namespace'

    def test_falls_back_to_env(self, monkeypatch):
        monkeypatch.setenv('NAMESPACE', 'env-namespace')
        with patch('builtins.open', side_effect=FileNotFoundError):
            assert announcement.get_namespace() == 'env-namespace'

    def test_defaults_to_repcal(self, monkeypatch):
        monkeypatch.delenv('NAMESPACE', raising=False)
        with patch('builtins.open', side_effect=FileNotFoundError):
            assert announcement.get_namespace() == 'repcal'


class TestGetWebhookUrls:
    def _mock_batch(self, cronjobs):
        mock_batch = MagicMock()
        mock_batch.list_namespaced_cron_job.return_value.items = cronjobs
        return mock_batch

    def test_extracts_urls(self):
        cjs = [
            make_mock_cronjob('https://discord.com/api/webhooks/1'),
            make_mock_cronjob('https://discord.com/api/webhooks/2'),
        ]
        with patch('announcement.config.load_incluster_config'), \
             patch('announcement.client.BatchV1Api', return_value=self._mock_batch(cjs)), \
             patch('announcement.get_namespace', return_value='repcal'):
            assert announcement.get_webhook_urls() == [
                'https://discord.com/api/webhooks/1',
                'https://discord.com/api/webhooks/2',
            ]

    def test_skips_cronjobs_without_webhook_url(self):
        cjs = [make_mock_cronjob(extra_env={'DB_PATH': '/data/calendar.db'})]
        with patch('announcement.config.load_incluster_config'), \
             patch('announcement.client.BatchV1Api', return_value=self._mock_batch(cjs)), \
             patch('announcement.get_namespace', return_value='repcal'):
            assert announcement.get_webhook_urls() == []

    def test_deduplicates_urls(self):
        url = 'https://discord.com/api/webhooks/1'
        cjs = [make_mock_cronjob(url), make_mock_cronjob(url), make_mock_cronjob(url)]
        with patch('announcement.config.load_incluster_config'), \
             patch('announcement.client.BatchV1Api', return_value=self._mock_batch(cjs)), \
             patch('announcement.get_namespace', return_value='repcal'):
            assert announcement.get_webhook_urls() == [url]

    def test_skips_containers_with_no_env(self):
        container = MagicMock()
        container.env = None
        cj = MagicMock()
        cj.spec.job_template.spec.template.spec.containers = [container]
        with patch('announcement.config.load_incluster_config'), \
             patch('announcement.client.BatchV1Api', return_value=self._mock_batch([cj])), \
             patch('announcement.get_namespace', return_value='repcal'):
            assert announcement.get_webhook_urls() == []


class TestEmbedOverrides:
    def _run(self, text, image_url='', urls=None):
        """Call announcement.run() and return the embed that was sent."""
        sent = []
        mock_hook = MagicMock()
        mock_hook.send.side_effect = lambda embed: sent.append(embed)

        with patch('announcement.get_data', return_value={}), \
             patch('announcement.construct_embed', return_value=Embed(title='old', description='old')), \
             patch('announcement.get_webhook_urls', return_value=urls or ['https://discord.com/api/webhooks/1']), \
             patch('announcement.SyncWebhook.from_url', return_value=mock_hook), \
             patch('builtins.open', mock_open(read_data=text)), \
             patch('announcement.ANNOUNCEMENT_IMAGE_URL', image_url):
            announcement.run()

        return sent[0] if sent else None

    def test_title_is_overridden(self):
        assert self._run('Some news').title == 'Une humble annonce'

    def test_description_is_announcement_text(self):
        assert self._run('Hello subscribers!').description == 'Hello subscribers!'

    def test_image_set_when_url_provided(self):
        embed = self._run('msg', image_url='https://example.com/img.jpg')
        assert embed.image.url == 'https://example.com/img.jpg'

    def test_image_not_set_when_url_empty(self):
        embed = self._run('msg', image_url='')
        assert not embed.image.url

    def test_sends_to_all_urls(self):
        sent = []
        mock_hook = MagicMock()
        mock_hook.send.side_effect = lambda embed: sent.append(embed)

        with patch('announcement.get_data', return_value={}), \
             patch('announcement.construct_embed', return_value=Embed()), \
             patch('announcement.get_webhook_urls', return_value=[
                 'https://discord.com/api/webhooks/1',
                 'https://discord.com/api/webhooks/2',
                 'https://discord.com/api/webhooks/3',
             ]), \
             patch('announcement.SyncWebhook.from_url', return_value=mock_hook), \
             patch('builtins.open', mock_open(read_data='msg')), \
             patch('announcement.ANNOUNCEMENT_IMAGE_URL', ''):
            announcement.run()

        assert mock_hook.send.call_count == 3


class TestSendBehavior:
    def test_exits_nonzero_on_any_failure(self):
        mock_hook = MagicMock()
        mock_hook.send.side_effect = Exception('404 Unknown Webhook')

        with patch('announcement.get_data', return_value={}), \
             patch('announcement.construct_embed', return_value=Embed()), \
             patch('announcement.get_webhook_urls', return_value=['https://discord.com/api/webhooks/bad']), \
             patch('announcement.SyncWebhook.from_url', return_value=mock_hook), \
             patch('announcement.write_failures_configmap'), \
             patch('builtins.open', mock_open(read_data='msg')), \
             patch('announcement.ANNOUNCEMENT_IMAGE_URL', ''):
            with pytest.raises(SystemExit) as exc:
                announcement.run()
            assert exc.value.code == 1

    def test_continues_after_failure_and_writes_configmap(self):
        mock_hook = MagicMock()
        mock_hook.send.side_effect = [Exception('404 Unknown Webhook'), None]

        mock_write = MagicMock()
        with patch('announcement.get_data', return_value={}), \
             patch('announcement.construct_embed', return_value=Embed()), \
             patch('announcement.get_webhook_urls', return_value=[
                 'https://discord.com/api/webhooks/bad',
                 'https://discord.com/api/webhooks/good',
             ]), \
             patch('announcement.SyncWebhook.from_url', return_value=mock_hook), \
             patch('announcement.write_failures_configmap', mock_write), \
             patch('builtins.open', mock_open(read_data='msg')), \
             patch('announcement.ANNOUNCEMENT_IMAGE_URL', ''):
            with pytest.raises(SystemExit):
                announcement.run()

        assert mock_hook.send.call_count == 2
        mock_write.assert_called_once_with(['https://discord.com/api/webhooks/bad'])
