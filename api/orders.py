"""
Vercel Serverless — 订单API
GET  /api/orders  → 获取所有订单
POST /api/orders  → 创建新订单
存储：Vercel KV Store
部署后在Vercel Dashboard中创建KV数据库并绑定到此项目
环境变量：KV_REST_API_URL, KV_REST_API_TOKEN
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime

KV_URL = os.environ.get('KV_REST_API_URL', '')
KV_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')
ORDERS_KEY = 'peach_orders'

# 内存兜底（KV不可用时使用，重启会丢失，仅应急）
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
    except Exception as e:
        print(f"[KV GET ERROR] {e}")
        return None

def kv_set(key, value):
    global _memory_fallback
    if not KV_URL or not KV_TOKEN:
        _memory_fallback = json.loads(value)
        return True
    try:
        url = f"{KV_URL}/set/{key}"
        body = json.dumps({"value": value}).encode()
        req = urllib.request.Request(url, data=body, method='POST', headers={
            "Authorization": f"Bearer {KV_TOKEN}",
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[KV SET ERROR] {e}")
        _memory_fallback = json.loads(value)
        return None


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        raw = kv_get(ORDERS_KEY)
        orders = json.loads(raw) if raw else []
        self.wfile.write(json.dumps(orders, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'

        try:
            data = json.loads(body)
        except:
            self._json_error(400, "无效的JSON数据")
            return

        required = ['spec', 'pricePerBox', 'quantity', 'peachTotal', 'province',
                     'address', 'shipping', 'packages', 'total', 'name', 'phone']
        for f in required:
            if f not in data:
                self._json_error(400, f"缺少必填字段: {f}")
                return

        raw = kv_get(ORDERS_KEY)
        orders = json.loads(raw) if raw else []

        new_id = (orders[-1]['id'] + 1) if orders else 1
        order = {
            "id": new_id,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "spec": data['spec'],
            "price_per_box": data['pricePerBox'],
            "quantity": data['quantity'],
            "peach_total": data['peachTotal'],
            "province": data['province'],
            "city": data.get('city', ''),
            "address": data['address'],
            "shipping": data['shipping'],
            "packages": data['packages'],
            "total": data['total'],
            "customer_name": data['name'],
            "customer_phone": data['phone']
        }
        orders.append(order)
        kv_set(ORDERS_KEY, json.dumps(orders, ensure_ascii=False))

        self.send_response(201)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"success": True, "id": new_id, "total": data['total']},
                                     ensure_ascii=False).encode('utf-8'))

    def _json_error(self, code, msg):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}, ensure_ascii=False).encode('utf-8'))
