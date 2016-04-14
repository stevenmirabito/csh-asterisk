from __future__ import print_function
import time
import threading
from slackclient import SlackClient

"""
Slack Bot for CSH PBX, based on SlackHQ's rtmbot
@author: Steven Mirabito <smirabito@csh.rit.edu>
"""


class SlackBot(threading.Thread):
    def __init__(self, token, channel_id):
        threading.Thread.__init__(self)

        self.last_ping = 0
        self.token = token
        self.channel_id = channel_id
        self.slack_client = None
        self.channel = None

    def connect(self):
        self.slack_client = SlackClient(self.token)
        self.slack_client.rtm_connect()
        self.channel = self.slack_client.server.channels.find(self.channel_id)

    def start(self):
        self.connect()
        while True:
            self.ping()
            time.sleep(.1)

    def ping(self):
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def output(self, message):
        if self.channel is not None and message is not None:
            message = message.encode('ascii', 'ignore')
            self.channel.send_message("{}".format(message))
