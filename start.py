import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Detect Keys purely from Render Environment Variables
gemini_key = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GOOGLE_API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or ""
).strip()

discord_token = (os.environ.get("DISCORD_BOT_TOKEN") or "").strip()
allowed_users = (os.environ.get("DISCORD_ALLOWED_USERS") or "*").strip()

# Gemini 2.5 Flash handles 1,000,000 tokens (easily fits 18k Hermes tool definitions)
selected_provider = "custom"
selected_base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
selected_model = "gemini-2.5-flash"
selected_key = gemini_key
selected_max_tokens = 8192

print(f"[Hermes Boot] Engine: Gemini 2.5 Flash (Key present: {'Yes' if selected_key else 'NO'})")

# Ensure /root/.hermes directory exists
os.makedirs("/root/.hermes", exist_ok=True)

# Write dynamic config.yaml
config_content = f"""database:
  journal_mode: wal
runtime:
  nofile_soft_limit: 4096
model:
  default: {selected_model}
  provider: {selected_provider}
  base_url: {selected_base_url}
  api_key: "{selected_key}"
  max_tokens: {selected_max_tokens}
discord:
  auto_thread: false
  require_mention: true
  allowed_users: ["*"]
group_sessions_per_user: true
"""
with open("/root/.hermes/config.yaml", "w", encoding="utf-8") as f:
    f.write(config_content)

# Write dynamic .env
with open("/root/.hermes/.env", "w", encoding="utf-8") as f:
    f.write(f"OPENAI_API_KEY={selected_key}\n")
    f.write(f"GEMINI_API_KEY={selected_key}\n")
    f.write(f"GOOGLE_API_KEY={selected_key}\n")
    f.write(f"DISCORD_BOT_TOKEN={discord_token}\n")
    f.write(f"DISCORD_ALLOWED_USERS={allowed_users}\n")
    f.write(f"GATEWAY_ALLOWED_USERS={allowed_users}\n")
    f.write("GATEWAY_ALLOW_ALL_USERS=true\n")
    f.write("DISCORD_AUTO_THREAD=false\n")

# Export for subprocess
os.environ["OPENAI_API_KEY"] = selected_key
os.environ["GEMINI_API_KEY"] = selected_key
os.environ["GOOGLE_API_KEY"] = selected_key
os.environ["DISCORD_BOT_TOKEN"] = discord_token
os.environ["DISCORD_ALLOWED_USERS"] = allowed_users
os.environ["GATEWAY_ALLOWED_USERS"] = allowed_users
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
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[Render Health Check] Web server listening on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()
    print("[Hermes Gateway] Starting Discord Gateway daemon...")
    subprocess.run(["hermes", "gateway", "run"])
