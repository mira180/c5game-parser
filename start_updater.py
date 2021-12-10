from updater.getter import Updater
from http.server import BaseHTTPRequestHandler, HTTPServer
from config import UPDATE_THREADS, UPDATE_INTERVAL, UPDATER_PORT
from constants import Platform
import json

updater = Updater([Platform.STEAM, Platform.C5GAME], threads=UPDATE_THREADS, interval=UPDATE_INTERVAL)

class ServerHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps((updater.statistics, updater.last_statistics)).encode())

if __name__ == '__main__':
    updater.start()
    server_address = ('', UPDATER_PORT)
    httpd = HTTPServer(server_address, ServerHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()