import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. Grab keys from Render environment variables
api_key = (
    os.environ.get("OPENAI_API_KEY")
    or os.environ.get("MODEL_API_KEY")
    or os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GOOGLE_API_KEY")
    or ""
).strip()

discord_token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()

print(f"[Hermes Boot] Found API Key: {'Yes (' + api_key[:6] + '...)' if api_key else 'NO - EMPTY'}")
print(f"[Hermes Boot] Found Discord Token: {'Yes' if discord_token else 'NO - EMPTY'}")

# 2. Ensure /root/.hermes directory exists
os.makedirs("/root/.hermes", exist_ok=True)

# 3. Explicitly write /root/.hermes/config.yaml with injected api_key
config_content = f"""database:
  journal_mode: wal
runtime:
  nofile_soft_limit: 4096
model:
  default: gemini-2.5-flash
  provider: custom
  base_url: https://generativelanguage.googleapis.com/v1beta/openai
  api_key: "{api_key}"
  max_tokens: 8192
discord:
  auto_thread: false
  require_mention: true
group_sessions_per_user: true
"""
with open("/root/.hermes/config.yaml", "w", encoding="utf-8") as f:
    f.write(config_content)

# 4. Explicitly write /root/.hermes/.env
with open("/root/.hermes/.env", "w", encoding="utf-8") as f:
    f.write(f"OPENAI_API_KEY={api_key}\n")
    f.write(f"GEMINI_API_KEY={api_key}\n")
    f.write(f"GOOGLE_API_KEY={api_key}\n")
    f.write(f"DISCORD_BOT_TOKEN={discord_token}\n")
    f.write("GATEWAY_ALLOW_ALL_USERS=true\n")
    f.write("DISCORD_AUTO_THREAD=false\n")

# 5. Export into environment for subprocess
os.environ["OPENAI_API_KEY"] = api_key
os.environ["GEMINI_API_KEY"] = api_key
os.environ["GOOGLE_API_KEY"] = api_key
os.environ["DISCORD_BOT_TOKEN"] = discord_token
os.environ["GATEWAY_ALLOW_ALL_USERS"] = "true"
os.environ["DISCORD_AUTO_THREAD"] = "false"

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
