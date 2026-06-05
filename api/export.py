"""
Vercel Serverless — CSV导出API
GET /api/export → 下载订单CSV文件
"""

import json
import os
import urllib.request
import csv
import io
from http.server import BaseHTTPRequestHandler

KV_URL = os.environ.get('KV_REST_API_URL', '')
KV_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')
ORDERS_KEY = 'peach_orders'

_memory_fallback = []

def kv_get(key):
    if not KV_URL or not KV_TOKEN:
        return json.dumps(_memory_fallback) if _memory_fallback else None
    try:
        url = f"{KV_URL}/get/{key}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KV_TOKEN}"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data.get('result')
    except:
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw = kv_get(ORDERS_KEY)
        orders = json.loads(raw) if raw else []

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
