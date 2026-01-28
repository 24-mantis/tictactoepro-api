from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client, Client
from urllib.parse import parse_qs, urlparse
from datetime import datetime

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
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            user_id = query.get('user_id', [None])[0]
            
            if not user_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing user_id"}).encode('utf-8'))
                return
            
            response = supabase.table('profiles').select('*').eq('user_id', user_id).execute()
            
            if response.data:
                profile = response.data[0]
            else:
                new_profile = {
                    'user_id': user_id,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                response = supabase.table('profiles').insert(new_profile).execute()
                profile = response.data[0]
            
            self._set_headers()
            self.wfile.write(json.dumps(profile).encode('utf-8'))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            
            user_id = body.get('user_id')
            if not user_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing user_id"}).encode('utf-8'))
                return
            
            update_data = {k: v for k, v in body.items() if k != 'user_id'}
            response = supabase.table('profiles').update(update_data).eq('user_id', user_id).execute()
            
            self._set_headers()
            self.wfile.write(json.dumps(response.data[0] if response.data else {}).encode('utf-8'))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
