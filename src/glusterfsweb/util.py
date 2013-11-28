# -*- coding: utf-8 -*-
"""
    util.py

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, GPL v2, see LICENSE for more details.
"""


class Notifications(object):
    def __init__(self):
        self.clients = list()

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def sendall(self, data):
        for client in self.clients:
            gevent.spawn(self.send, client, data)
