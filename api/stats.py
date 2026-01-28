from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        try:
            response = supabase.table('global_stats').select('*').eq('id', 1).execute()
            stats = response.data[0] if response.data else {}
            
            self._set_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            
            supabase.table('global_stats').update(body).eq('id', 1).execute()
            
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
