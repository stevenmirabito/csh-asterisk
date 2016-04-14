#!/usr/bin/python

"""
FastAGI Interface for CSH PBX
@author: Steven Mirabito <smirabito@csh.rit.edu>
"""

import re
import threading
import pystrix
import yaml
import time
from argparse import ArgumentParser
from slack import SlackBot


class FastAGIServer(threading.Thread):
    """
    A simple thread that runs a FastAGI server forever.
    """
    _fagi_server = None  # The FastAGI server controlled by this thread

    def __init__(self, config):
        threading.Thread.__init__(self)
        self.daemon = True

        # Initialize Slack client
        self.slack_client = SlackBot(config["SLACK_TOKEN"], config["SLACK_CHANNEL"]).start()

        # Initialize FastAGI server
        self._fagi_server = pystrix.agi.FastAGIServer(interface='127.0.0.1', port=35498)

        # Register Handlers
        self._fagi_server.register_script_handler(re.compile('demo'), self._demo_handler)
        self._fagi_server.register_script_handler(re.compile('slack'), self._notify_slack)
        # self._fagi_server.register_script_handler(re.compile('welcome'), self._welcome_handler)
        self._fagi_server.register_script_handler(None, self._noop_handler)

    @staticmethod
    def _demo_handler(agi, args, kwargs, match, path):
        """
        `agi` is the AGI instance used to process events related to the channel, `args` is a
        collection of positional arguments provided with the script as a tuple, `kwargs` is a
        dictionary of keyword arguments supplied with the script (values are enumerated in a list),
        `match` is the regex match object (None if the fallback handler), and `path` is the string
        path supplied by Asterisk, in case special processing is needed.

        The directives issued in this function can all raise Hangup exceptions, which should be
        caught if doing anything complex, but an uncaught exception will simply cause a warning to
        be raised, making AGI scripts very easy to write.
        """
        agi.execute(pystrix.agi.core.Answer())  # Answer the call

        response = agi.execute(pystrix.agi.core.StreamFile('demo-thanks', escape_digits=(
            '1', '2')))  # Play a file; allow DTMF '1' or '2' to interrupt
        if response:  # Playback was interrupted; if you don't care, you don't need to catch this
            (dtmf_character, offset) = response  # The key pressed by the user and the playback time

        agi.execute(pystrix.agi.core.Hangup())  # Hang up the call

    def _notify_slack(self, agi, args, kwargs, match, path):
        agi.execute(pystrix.agi.core.Answer())
        self.slack_client.output("@channel: An elevator has been requested. Please send one down ASAP. Thanks!")
        agi.execute(pystrix.agi.core.Hangup())

    """
    @staticmethod
    def _welcome_handler(agi, args, kwargs, match, path):
        # Create a connection to the CSH LDAP server
        ldap = CSHLDAP.CSHLDAP('<username>', '<password>', simple=True)

        # Get the user's phone number from caller ID
        callerid_number = '902'

        # Search LDAP for a member with this phone number
        search = ldap.search(mobile=callerid_number)

        # Convert the response to a list of member objects
        search_results = ldap.memberObjects(search)

        # Only continue if we found a member
        if len(search_results) > 0:
            # Grab the first member object returned
            member = search_results[0]
            member_attr = member.fields()

            # Figure out the member's active/on-floor status
            member_status = ''

            if member.isActive():
                member_status += 'active, '
            else:
                member_status += 'inactive, '

            if member.isOnFloor():
                member_status += 'on floor'
            else:
                member_status += 'off floor'

            # Construct and return the welcome message
            agi.execute(pystrix.agi.core.SetVariable('WELCOME',
                                                     'Hello ' + member.fullName() + '! According to my records, you are currently an ' + member_status + ' member, with ' +
                                                     member_attr['drink_balance'] + ' drink credits.'))
    """

    @staticmethod
    def _noop_handler(self, agi, args, kwargs, match, path):
        """
        Does nothing, causing control to return to Asterisk's dialplan immediately; provided just
        to demonstrate the fallback handler.
        """
        pass

    def kill(self):
        self._fagi_server.shutdown()

    def run(self):
        self._fagi_server.serve_forever()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
            '-c',
            '--config',
            help='Full path to config file.',
            metavar='path'
    )
    return parser.parse_args()


if __name__ == '__main__':
    # Load config
    args = parse_args()
    srv_config = yaml.load(file(args.config or 'csh-asterisk.conf', 'r'))

    # Initialize and start FastAGI server
    fastagi_core = FastAGIServer(srv_config)
    fastagi_core.start()

    while fastagi_core.is_alive():
        time.sleep(.1)

    fastagi_core.kill()
