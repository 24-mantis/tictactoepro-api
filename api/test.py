from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "OK",
            "message": "Тестовый эндпоинт работает!",
            "version": "1.0"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
