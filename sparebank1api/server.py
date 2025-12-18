from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any


def callbackhandler_factory(res: dict[Any, Any]):
    class CallbackHandler(BaseHTTPRequestHandler):
        res: dict[Any, Any] = {}

        def do_GET(self):
            self.res["path"] = self.path
            self.res["headers"] = str(self.headers)
            return self.wfile.write("Ok".encode("utf8"))

    CallbackHandler.res = res
    return CallbackHandler


def wait_for_callback(port: int = 8080):
    server_address = ("", port)
    res: dict[str, Any] = {}
    httpd = HTTPServer(server_address, callbackhandler_factory(res))
    httpd.handle_request()
    return res
