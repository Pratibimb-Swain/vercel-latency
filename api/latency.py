from http.server import BaseHTTPRequestHandler
import json
import numpy as np

# CORS Headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}

# Load telemetry data
with open("q-vercel-latency.json") as f:
    data = json.load(f)


class handler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        request = json.loads(body)

        regions = request["regions"]
        threshold = request["threshold_ms"]

        result = {}

        for region in regions:
            region_data = [r for r in data if r["region"] == region]

            latencies = [r["latency_ms"] for r in region_data]
            uptimes = [r["uptime"] for r in region_data]

            result[region] = {
                "avg_latency": float(np.mean(latencies)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "avg_uptime": float(np.mean(uptimes)),
                "breaches": sum(1 for l in latencies if l > threshold),
            }

        self._set_headers()
        self.wfile.write(json.dumps(result).encode())
