"""The base plugin for polyphemus.

This module is available as an polyphemus plugin by the name ``polyphemus.base``.

Base Plugin API
===============
"""
from __future__ import print_function
import re
import os
import sys
import socket
from warnings import warn

if sys.version_info[0] >= 3:
    basestring = str
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

try:
    import simplejson as json
except ImportError:
    import json

from .utils import RunControl, NotSpecified, writenewonly, \
    DEFAULT_RC_FILE, DEFAULT_PLUGINS, nyansep, indent
from .plugins import Plugin
from .version import report_versions

ENDS_PORT_RE = re.compile('(.*)(:)(\d+)')

class PolyphemusPlugin(Plugin):
    """This class provides base functionality for polyhemus itself."""

    defaultrc = RunControl(
        rc=DEFAULT_RC_FILE,
        plugins=DEFAULT_PLUGINS,
        debug=False,
        debug_filename='debug.txt',
        verbose=False,
        version=False,
        bash_completion=True,
        host='0.0.0.0',
        port=80,
        appname="polyphemus",
        server_url=NotSpecified,
        )

    rcdocs = {
        'rc': "Path to run control file",
        'plugins': "Plugins to include",
        'debug': 'run in debugging mode', 
        'debug_filename': 'the path to the debug file', 
        'verbose': "Print more output.",
        'version': "Print version information.",
        'bash_completion': ("Flag for enabling / disabling BASH completion. "
                            "This is only relevant when using argcomplete."),
        'host': ("Which urls to host to, ie '0.0.0.0' for everyone or "
                 "'localhost' for yourself"),
        'port': "The port to run the application on.",
        'appname': "The name of the flask application.",
        'server_url': ("The URL of the server without a trailing slash or port "
                       "number, eg 'http://pynesim.org'. If not provided, it will "
                       "be guessed from your current public IP address."),
        }

    def update_argparser(self, parser):
        parser.add_argument('--rc', help=self.rcdocs['rc'])
        parser.add_argument('--plugins', nargs="+", help=self.rcdocs["plugins"])
        parser.add_argument('--debug', action='store_true', 
                            help=self.rcdocs["debug"])
        parser.add_argument('--debug-filename', dest='debug_filename', 
                            help=self.rcdocs["debug_filename"])
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                            help=self.rcdocs["verbose"])
        parser.add_argument('--version', action='store_true', dest='version',
                            help=self.rcdocs["version"])
        parser.add_argument('--host', help=self.rcdocs['host'])
        parser.add_argument('--port', help=self.rcdocs['port'])
        parser.add_argument('--appname', help=self.rcdocs['appname'])
        parser.add_argument('--server-url', dest='server_url', 
                            help=self.rcdocs["server_url"])

    def setup(self, rc):
        if rc.version:
            print(report_versions())
            sys.exit()
        rc.port = int(rc.port)
        rc.rc = os.path.abspath(rc.rc)

        # set server_url
        server_url = rc.server_url
        if server_url is NotSpecified:
            jsonip = urlopen('http://jsonip.com/')
            ipinfo = json.load(jsonip)
            ipaddr = ipinfo['ip']
            try:
                server_url, aliases, ips = socket.gethostbyaddr(ipaddr)
            except socket.herror:
                server_url, aliases, ips = 'http://' + ipaddr, (), ()
            print("server_url not specified, guessing " + server_url)
            if rc.verbose:
                print("Other server_url options:\n  " + "\n  ".join(aliases + ips))
        else:
            if server_url.endswith('/'):
                server_url = server_url[:-1]
            m = ENDS_PORT_RE.match(server_url)
            if m is not None:
                server_url = m.group(1)
        if not server_url.startswith('http://') and \
           not server_url.startswith('https://'):
            server_url = 'http://' + server_url
        rc.server_url = server_url

    def report_debug(self, rc):
        msg = 'Version Information:\n\n{0}\n\n'
        msg += nyansep + "\n\n"
        return msg

