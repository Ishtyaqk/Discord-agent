import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hermes Discord Agent is Online 24/7!\n")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Silent health checks to keep logs clean

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[Render Health Check] Web server listening on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Start lightweight HTTP server for Render port binding
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()

    # Run the Hermes Discord Gateway
    print("[Hermes Gateway] Starting Discord Gateway daemon...")
    subprocess.run(["hermes", "gateway", "run"])
