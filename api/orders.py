"""
Vercel Serverless — 订单API (Supabase版)
GET  /api/orders  → 获取所有订单
POST /api/orders  → 创建新订单
"""
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = "https://zwixfkrayawfroboplcw.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3aXhma3JheWF3ZnJvYm9wbGN3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4NjQ5NTUsImV4cCI6MjA5NjQ0MDk1NX0.kG1z9KRv0D2DXZm6yEgmBatlGgtXOewN43M4xXgZH6M")

def supabase_request(method, path, body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else []

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            orders = supabase_request("GET", "orders?select=*&order=id.desc")
        except Exception as e:
            orders = []
        self._json(200, orders)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            data = json.loads(body)
        except:
            self._json(400, {"error": "无效的JSON数据"})
            return

        row = {
            "spec": data.get("spec",""),
            "price_per_box": data.get("pricePerBox",0),
            "quantity": data.get("quantity",0),
            "peach_total": data.get("peachTotal",0),
            "province": data.get("province",""),
            "city": data.get("city",""),
            "address": data.get("address",""),
            "shipping": data.get("shipping",0),
            "packages": data.get("packages",0),
            "total": data.get("total",0),
            "customer_name": data.get("name",""),
            "customer_phone": data.get("phone","")
        }
        try:
            result = supabase_request("POST", "orders", row)
            new_id = result[0]["id"] if result else 0
        except Exception as e:
            self._json(500, {"error": str(e)})
            return
        self._json(201, {"success": True, "id": new_id, "total": data.get("total",0)})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
