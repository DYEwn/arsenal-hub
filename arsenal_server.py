#!/usr/bin/env python3
"""
Arsenal Hub - Cloud Server (Railway 배포용)
"""

import http.server
import urllib.request
import urllib.parse
import json
import os

# Railway는 환경변수로 API 키와 PORT를 넘김
API_KEY = os.environ.get("FD_API_KEY", "")
PORT = int(os.environ.get("PORT", 8080))

class ArsenalProxy(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{self.path}] {format % args}")

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        # Serve HTML
        if self.path == "/" or self.path == "/arsenal_hub_v2.html":
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arsenal_hub_v2.html")
            if os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_cors()
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"arsenal_hub_v2.html not found")
            return

        # API proxy
        if self.path.startswith("/api/"):
            api_path = self.path[4:]
            url = f"https://api.football-data.org/v4{api_path}"
            try:
                req = urllib.request.Request(url, headers={"X-Auth-Token": API_KEY})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = r.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as e:
                body = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # AllSports proxy
        if self.path.startswith("/allsports/"):
            api_path = self.path[len("/allsports"):]
            url = f"https://allsportsapi2.p.rapidapi.com{api_path}"
            try:
                req = urllib.request.Request(url, headers={
                    "x-rapidapi-host": "allsportsapi2.p.rapidapi.com",
                    "x-rapidapi-key": "692d7efbe5mshb82d488afe6642ap189e0ajsn0d594bdfb79f"
                })
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = r.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as e:
                body = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # RSS proxy
        if self.path.startswith("/rss"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            feed_url = params.get("url", [""])[0]
            if feed_url:
                try:
                    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=8) as r:
                        data = r.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/xml")
                    self.send_cors()
                    self.end_headers()
                    self.wfile.write(data)
                except Exception as e:
                    self.send_response(500)
                    self.send_cors()
                    self.end_headers()
            return

        self.send_error(404)

if __name__ == "__main__":
    if not API_KEY:
        print("⚠️  FD_API_KEY 환경변수가 없어요.")
    server = http.server.HTTPServer(("0.0.0.0", PORT), ArsenalProxy)
    print(f"✅ Arsenal Hub 서버 시작! PORT={PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("서버 종료됨.")
