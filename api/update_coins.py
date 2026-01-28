from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            
            user_id = body.get('user_id')
            amount = body.get('amount')
            reason = body.get('reason', '')
            
            if not user_id or amount is None:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing user_id or amount"}).encode('utf-8'))
                return
            
            response = supabase.table('profiles').select('coins, total_coins_earned').eq('user_id', user_id).execute()
            
            if not response.data:
                self._set_headers(404)
                self.wfile.write(json.dumps({"success": False, "error": "Profile not found"}).encode('utf-8'))
                return
            
            current_coins = response.data[0]['coins']
            new_balance = current_coins + amount
            
            if new_balance < 0:
                self._set_headers(200)
                self.wfile.write(json.dumps({"success": False, "error": "Insufficient funds"}).encode('utf-8'))
                return
            
            update_data = {'coins': round(new_balance, 2)}
            
            if amount > 0:
                total_earned = response.data[0]['total_coins_earned']
                update_data['total_coins_earned'] = total_earned + amount
            
            supabase.table('profiles').update(update_data).eq('user_id', user_id).execute()
            
            supabase.table('transactions').insert({
                'user_id': user_id,
                'amount': amount,
                'reason': reason,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }).execute()
            
            self._set_headers()
            self.wfile.write(json.dumps({"success": True, "new_balance": round(new_balance, 2)}).encode('utf-8'))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
