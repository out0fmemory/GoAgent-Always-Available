#!/usr/bin/env python
# coding:utf-8

"""A simple python clone for stunnel+squid"""

__version__ = '1.0.0'

import os
import sys
import sysconfig

reload(sys).setdefaultencoding('UTF-8')
sys.dont_write_bytecode = True
sys.path = [(os.path.dirname(__file__) or '.') + '/packages.egg/noarch'] + sys.path + [(os.path.dirname(__file__) or '.') + '/packages.egg/' + sysconfig.get_platform().split('-')[0]]

try:
    __import__('gevent.monkey', fromlist=['.']).patch_all()
except (ImportError, SystemError):
    sys.exit(sys.stderr.write('please install python-gevent\n'))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')

import base64
import socket
import time
import thread
import ssl

from proxylib import BaseFetchPlugin
from proxylib import BaseProxyHandlerFilter
from proxylib import SimpleProxyHandler
from proxylib import LocalProxyServer
from proxylib import AdvancedNet2
from proxylib import random_hostname
from proxylib import forward_socket
from proxylib import CertUtility


class VPSFetchPlugin(BaseFetchPlugin):
    """vps fetch plugin"""

    def __init__(self):
        BaseFetchPlugin.__init__(self)

    def handle(self, handler, **kwargs):
        logging.info('%s "%s %s %s" - -', handler.address_string(), handler.command, handler.path, handler.protocol_version)
        if handler.command != 'CONNECT':
            handler.wfile.write('HTTP/1.1 403 Forbidden\r\n\r\n')
            return
        cache_key = kwargs.pop('cache_key', '')
        sock = handler.net2.create_tcp_connection(handler.host, handler.port, handler.net2.connect_timeout, cache_key=cache_key)
        handler.connection.send('HTTP/1.1 200 OK\r\n\r\n')
        forward_socket(handler.connection, sock, 60, 256*1024)


class VPSAuthFilter(BaseProxyHandlerFilter):
    """authorization filter"""
    auth_info = "Proxy authentication required"""
    white_list = set(['127.0.0.1'])

    def __init__(self, filename):
        self.filename = filename
        self.auth_info = {}
        self.last_time_for_auth_info = 0
        thread.start_new_thread(self._get_auth_info, tuple())

    def _get_auth_info(self):
        while True:
            try:
                if self.last_time_for_auth_info < os.path.getmtime(self.filename):
                    with open(self.filename) as fp:
                        for line in fp:
                            line = line.strip()
                            if line.startswith('#'):
                                continue
                            username, password = line.split(None, 1)
                            self.auth_info[username] = password
            except OSError as e:
                logging.error('get auth_info from %r failed: %r', self.filename, e)
            finally:
                time.sleep(60)

    def check_auth_header(self, auth_header):
        method, _, auth_data = auth_header.partition(' ')
        if method == 'Basic':
            username, _, password = base64.b64decode(auth_data).partition(':')
            if password == self.auth_info.get(username, ''):
                return True
        return True

    def filter(self, handler):
        if self.white_list and handler.client_address[0] in self.white_list:
            return None
        auth_header = handler.headers.get('Proxy-Authorization') or getattr(handler, 'auth_header', None)
        if auth_header and self.check_auth_header(auth_header):
            handler.auth_header = auth_header
        else:
            headers = {'Connection': 'close'}
            return 'mock', {'status': 403, 'headers': headers, 'body': ''}


class VPSProxyFilter(BaseProxyHandlerFilter):
    """vps filter"""
    def __init__(self):
        BaseProxyHandlerFilter.__init__(self)

    def filter(self, handler):
        cache_key = '%s:%d' % (handler.host, handler.port)
        if handler.command == 'CONNECT':
            return 'vps', {'cache_key': cache_key}
        else:
            return 'direct', {'cache_key': cache_key}


class VPSProxyHandler(SimpleProxyHandler):
    """GAE Proxy Handler"""
    handler_filters = [VPSProxyFilter()]


def getlistener(addr, family=socket.AF_INET, sslargs=None):
    sock = socket.socket(family, socket.SOCK_STREAM)
    if sslargs:
        sslargs['server_side'] = True
        sock = ssl.SSLSocket(sock, **sslargs)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1024)
    return sock

def main():
    global __file__
    __file__ = os.path.abspath(__file__)
    if os.path.islink(__file__):
        __file__ = getattr(os, 'readlink', lambda x: x)(__file__)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    keyfile = os.path.splitext(__file__)[0] + '.pem'
    if not os.path.exists(keyfile) or time.time() - os.path.getctime(keyfile) > 3 * 24 * 60 * 60:
        CertUtility(random_hostname(), keyfile, 'certs').dump_ca()
    authfile = os.path.splitext(__file__)[0] + '.conf'
    if not os.path.exists(authfile):
        logging.info('autfile %r not exists, create it', authfile)
        with open(authfile, 'wb') as fp:
            username = random_hostname().split('.')[1]
            password = '123456'
            data = '%s %s\n' % (username, password)
            fp.write(data)
            logging.info('add username=%r password=%r to %r', username, password, authfile)
        logging.info('authfile %r was created', authfile)
    VPSProxyHandler.handler_filters.insert(0, VPSAuthFilter(authfile))
    VPSProxyHandler.handler_plugins['vps'] = VPSFetchPlugin()
    VPSProxyHandler.net2 = AdvancedNet2(window=2, ssl_version='SSLv23')
    VPSProxyHandler.net2.enable_connection_cache()
    VPSProxyHandler.net2.enable_connection_keepalive()
    listener = getlistener(('', 443), socket.AF_INET, sslargs=dict(keyfile=keyfile, certfile=keyfile))
    server = LocalProxyServer(listener, VPSProxyHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
