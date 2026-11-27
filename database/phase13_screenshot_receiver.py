"""Temporary localhost receiver for genuine Phase 13 browser screenshots."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DESTINATION = Path(__file__).resolve().parents[1] / 'screenshots' / 'final'
DESTINATION.mkdir(parents=True, exist_ok=True)


class ScreenshotReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        name = Path(self.path).name
        if not name.startswith('phase13_') or not name.endswith(('.png', '.jpg', '.jpeg')):
            self.send_error(400, 'Invalid screenshot filename')
            return
        image = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        valid_png = image.startswith(b'\x89PNG\r\n\x1a\n')
        valid_jpeg = image.startswith(b'\xff\xd8\xff')
        if not (valid_png or valid_jpeg):
            self.send_error(415, 'Expected PNG or JPEG bytes')
            return
        (DESTINATION / name).write_bytes(image)
        self.send_response(201)
        self.end_headers()
        self.wfile.write(b'saved')

    def log_message(self, *_args):
        pass


HTTPServer(('127.0.0.1', 8768), ScreenshotReceiver).serve_forever()
