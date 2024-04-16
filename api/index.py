from http.server import BaseHTTPRequestHandler
from src.app import create_patrol_app
import json

app = create_patrol_app()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = json.dumps({'message': 'Hello from Python on Vercel!'})
        self.wfile.write(message.encode())
        return