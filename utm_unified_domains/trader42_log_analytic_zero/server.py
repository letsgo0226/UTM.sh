from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import socket
import threading
from core import PROTOCOL, MAX_JSON_BYTES, evaluate, transition, encode_payload, manifest


def pairs(items):
    d = {}
    for k, v in items:
        if k in d:
            raise ValueError("duplicate JSON key")
        d[k] = v
    return d


def invalid_constant(value):
    raise ValueError("nonfinite JSON number")


class BoundedServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16

    def __init__(self, address, handler):
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(address, handler)

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(5)
        return connection, address

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            try:
                request.sendall(b"HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()


class H(BaseHTTPRequestHandler):
    def sendj(self, status, value):
        b = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        if self.headers.get("Transfer-Encoding"):
            raise ValueError("Transfer-Encoding is not supported")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not lengths[0].isdigit():
            raise ValueError("one valid Content-Length is required")
        n = int(lengths[0])
        if n == 0 or n > MAX_JSON_BYTES:
            raise ValueError("body must contain 1 to 16384 bytes")
        raw = self.rfile.read(n)
        if len(raw) != n:
            raise ValueError("incomplete body")
        d = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
        if not isinstance(d, dict):
            raise ValueError("payload must be an object")
        return d

    def do_GET(self):
        if self.path == "/health":
            self.sendj(200, {"ok": True, "protocol": PROTOCOL, "commit": os.getenv("RAILWAY_GIT_COMMIT_SHA", os.getenv("RENDER_GIT_COMMIT", "unknown"))})
        elif self.path == "/manifest":
            self.sendj(200, manifest())
        else:
            self.sendj(404, {"error": "not-found"})

    def do_POST(self):
        try:
            handlers = {"/evaluate": evaluate, "/transition": transition}
            if self.path not in (*handlers, "/encode"):
                self.sendj(404, {"error": "not-found"})
                return
            d = self.body()
            if self.path == "/encode":
                if "payload" not in d:
                    raise ValueError("missing required field: payload")
                result = encode_payload(d["payload"])
            else:
                result = handlers[self.path](d)
            self.sendj(200, result)
        except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError) as exc:
            self.sendj(400, {"error": str(exc), "protocol": PROTOCOL, "decision": "REJECTED_INPUT"})
        except (socket.timeout, TimeoutError):
            self.sendj(408, {"error": "request-timeout", "protocol": PROTOCOL})
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt % args), flush=True)


if __name__ == "__main__":
    BoundedServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), H).serve_forever()
