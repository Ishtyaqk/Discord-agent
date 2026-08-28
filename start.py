import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Bridge environment variables for Hermes custom provider
gemini_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("MODEL_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if gemini_key:
    os.environ["OPENAI_API_KEY"] = gemini_key
    os.environ["GEMINI_API_KEY"] = gemini_key
    os.environ["GOOGLE_API_KEY"] = gemini_key

if "OPENAI_BASE_URL" not in os.environ:
    os.environ["OPENAI_BASE_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai"

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
        pass  # Silent health checks

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
