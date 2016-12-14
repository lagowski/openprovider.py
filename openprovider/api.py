# coding=utf-8

"""
Entry point for the OpenProvider API.
"""

import lxml
import lxml.objectify
import lxml.etree
import os
import requests

from openprovider.data.exception_map import from_code
from openprovider.exceptions import ServiceUnavailable
from openprovider.modules import E, OE, MODULE_MAPPING
from openprovider.response import Response


HOOKS = ['pre_request', 'post_request']


def _get_module_name(module):
    """
    Return the module name.

    >>> from openprovider.modules import CustomerModule
    >>> _get_module_name(CustomerModule)
    'customer'

    >>> _get_module_name(OpenProvider)
    'openprovider'
    """
    name = module.__name__[:-6] if module.__name__.endswith('Module') else module.__name__
    return name.lower()


class OpenProvider(object):
    """A connection to the OpenProvider API."""

    def __init__(self, username, password=None, url="https://api.openprovider.eu",
            password_hash=None, hooks=None):
        """Initializes the connection with the given username and password."""

        if bool(password) == bool(password_hash):
            raise ValueError('Provide either a password or a password hash')

        self.username = username
        self.password = password
        self.password_hash = password_hash
        self.url = url

        # Set up the API client
        self.session = requests.Session()
        self.session.verify = True
        self.session.headers['User-Agent'] = 'openprovider.py/0.10.4'

        # Initialize and add all modules.
        for old_name, module in MODULE_MAPPING.items():
            name = _get_module_name(module)
            instance = module(self)
            setattr(self, name, instance)
            if old_name != name:
                setattr(self, old_name, instance)

        hooks = hooks or {}
        self.hooks = {hook: hooks.get(hook) for hook in HOOKS}

    def request(self, tree, **kwargs):
        """
        Construct a new request with the given tree as its contents, then ship
        it to the OpenProvider API.
        """

        apirequest = lxml.etree.tostring(
            E.openXML(
                E.credentials(
                    E.username(self.username),
                    OE('password', self.password),
                    OE('hash', self.password_hash),
                ),
                tree
            ),

            method='c14n'
        )

        self._run_hook('pre_request', tree, apirequest)

        try:
            apiresponse = self.session.post(self.url, data=apirequest)
            apiresponse.raise_for_status()
        except requests.RequestException as e:
            raise ServiceUnavailable(str(e))

        responsetree = lxml.objectify.fromstring(apiresponse.content)
        self._run_hook('post_request', apiresponse, responsetree)

        if responsetree.reply.code == 0:
            return Response(responsetree)
        else:
            klass = from_code(responsetree.reply.code)
            desc = responsetree.reply.desc
            code = responsetree.reply.code
            data = getattr(responsetree.reply, 'data', '')
            raise klass("{0} ({1}) {2}".format(desc, code, data), code)

    def _run_hook(self, hook, *args, **kwargs):
        callback = self.hooks[hook]
        if callback:
            callback(*args, **kwargs)


def _get_env(key, account):
    env_key = account.upper() + '_' if account else ''
    try:
        return os.environ['OPENPROVIDER_' + env_key + key.upper()]
    except KeyError:
        msg = 'Missing openprovider ' + key
        if account:
            msg += ' for account ' + account
        raise KeyError(msg)


def api_factory(account=''):
    username = _get_env('username', account)
    try:
        password_hash = _get_env('password_hash', account)
        password = None
    except KeyError:
        password_hash = None
        password = _get_env('password', account)
    url = os.environ.get('OPENPROVIDER_URL', 'https://api.openprovider.eu')

    return OpenProvider(username=username, password=password, password_hash=password_hash, url=url)
