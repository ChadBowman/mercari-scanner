import requests
import logging

log = logging.getLogger(__name__)


class Slack:
    BASE = 'https://slack.com/api/'

    def __init__(self, token):
        self.token = token
        self.channels = {}

    def send_message(self, channel, text):
        id = self._fetch_channel_id(channel)
        if not id:
            return
        body = {'channel': id, 'text': text}
        self._post('chat.postMessage', body)

    def _fetch_channel_id(self, channel):
        channel_id = self.channels.get(channel, None)
        if not channel_id:
            result = self._get('conversations.list').json()
            if not result['ok'] or not result['channels']:
                log.error("There was an issue fetching the channel id, please double-check "
                          "your credentials and try again")
                return None
            channels = result['channels']
            channels_with_name = list(filter(lambda x: x['name'] == channel, channels))
            if not channels_with_name:
                log.error(f"No channel found with name: {channel}")
            else:
                channel_id = channels_with_name[0]['id']
        return channel_id

    def _get(self, path):
        headers = {'Authorization': f"Bearer {self.token}"}
        return requests.get(SlackAlerter.BASE + path, headers=headers)

    def _post(self, path, body):
        headers = {'Authorization': f"Bearer {self.token}"}
        return requests.post(SlackAlerter.BASE + path, headers=headers, json=body)


class SlackAlerter(Slack):
    BASE = 'https://slack.com/api/'

    def __init__(self, token, channel):
        Slack.__init__(self, token)
        self.channel = channel

    def alert(self, text):
        log.info(f"Alerting: {text}")
        self.send_message(self.channel, text)
