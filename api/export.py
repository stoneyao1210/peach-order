"""
Vercel Serverless — CSV导出API (Supabase版)
GET /api/export → 下载订单CSV
"""
import json, os, urllib.request, csv, io
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = "https://zwixfkrayawfroboplcw.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3aXhma3JheWF3ZnJvYm9wbGN3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4NjQ5NTUsImV4cCI6MjA5NjQ0MDk1NX0.kG1z9KRv0D2DXZm6yEgmBatlGgtXOewN43M4xXgZH6M")

def supabase_request(method, path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            orders = supabase_request("GET", "orders?select=*&order=id.desc")
        except:
            orders = []

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['编号','时间','规格','单价','数量','桃子金额',
                         '省份','城市','地址','邮费','快递单数','总价',
                         '收件人','手机'])
        for o in orders:
            writer.writerow([
                o.get('id',''), o.get('created_at',''), o.get('spec',''),
                o.get('price_per_box',''), o.get('quantity',''),
                o.get('peach_total',''), o.get('province',''),
                o.get('city',''), o.get('address',''),
                o.get('shipping',''), o.get('packages',''),
                o.get('total',''),
                o.get('customer_name',''), o.get('customer_phone','')
            ])

        csv_bytes = output.getvalue().encode('utf-8-sig')
        self.send_response(200)
        self.send_header('Content-Type', 'text/csv; charset=utf-8-sig')
        self.send_header('Content-Disposition', 'attachment; filename="orders.csv"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(csv_bytes)))
        self.end_headers()
        self.wfile.write(csv_bytes)
