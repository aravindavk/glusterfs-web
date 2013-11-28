# -*- coding: utf-8 -*-
"""
    glusterweb.py

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, GPL v2, see LICENSE for more details.
"""
import argparse
from flask import Flask, render_template, Response
import sys
import json
import os
import nodestatedb as _db
from config import DB_FILE, DEBUG
import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from util import Notifications


app = Flask(__name__)
app.debug = DEBUG
notifications = Notifications()
args = ()


def _get_args():
    parser = argparse.ArgumentParser(description='GlusterFS Web')
    # parser.add_argument('username', type=str, help="UserName")
    # parser.add_argument('password', type=str, help="Password")
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='Port for dashboard(default is 8080)')

    return parser.parse_args()


@app.route("/")
def home():
    return render_template("index.html", port=args.port)


@app.route("/volumes")
def get_volumes_list():
    _db.connect(DB_FILE)
    return Response(json.dumps(_db.get_volumes()),
                    mimetype='application/json')


@app.route('/notify/<change>')
def notify(change):
    notifications.sendall("change")
    return "OK"


def handle_websocket(ws):
    notifications.register(ws)

    while True:
        message = ws.receive()
        if message is None:
            break
        ws.send("change")


def wsgi_app(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/watch":
        handle_websocket(environ["wsgi.websocket"])
    else:
        return app(environ, start_response)


def main():
    host = "localhost"
    global args
    args = _get_args()
    url_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "data",
                            "url")
    with open(url_file, "w") as f:
        f.write("http://%s:%s/notify" % (host, args.port))

    url_message = "http://%s" % host
    if args.port != 80:
        url_message += ":%s" % args.port

    sys.stdout.write("\n\n----------------\n\n")
    sys.stdout.write("GlusterWeb is available ")
    sys.stdout.write("in %s\n" % url_message)
    # sys.stdout.write("Use the username and password you provided to login")
    sys.stdout.write("\n\n----------------\n\n")
    http_server = WSGIServer((host, args.port),
                             wsgi_app,
                             handler_class=WebSocketHandler)
    http_server.serve_forever()
