from http.server import BaseHTTPRequestHandler
import json
import numpy as np

# Load telemetry data
with open("q-vercel-latency.json") as f:
    data = json.load(f)

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
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
                "breaches": sum(1 for l in latencies if l > threshold)
            }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(json.dumps(result).encode())