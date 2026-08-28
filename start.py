import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. Grab environment variables
gemini_key = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GOOGLE_API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or ""
).strip()

discord_token = (os.environ.get("DISCORD_BOT_TOKEN") or "").strip()
allowed_users = (os.environ.get("DISCORD_ALLOWED_USERS") or "*").strip()

hermes_dir = os.path.expanduser("~/.hermes")
os.makedirs(hermes_dir, exist_ok=True)

# 2. Write dynamic config.yaml
config_content = f"""database:
  journal_mode: wal
runtime:
  nofile_soft_limit: 4096
model:
  default: gemini-2.5-flash
  provider: custom
  base_url: https://generativelanguage.googleapis.com/v1beta/openai
  api_key: "{gemini_key}"
  max_tokens: 8192
discord:
  auto_thread: false
  require_mention: true
  allowed_users: ["*"]
group_sessions_per_user: true
"""
with open(os.path.join(hermes_dir, "config.yaml"), "w", encoding="utf-8") as f:
    f.write(config_content)

# 3. Write dynamic .env
with open(os.path.join(hermes_dir, ".env"), "w", encoding="utf-8") as f:
    f.write(f"OPENAI_API_KEY={gemini_key}\n")
    f.write(f"GEMINI_API_KEY={gemini_key}\n")
    f.write(f"GOOGLE_API_KEY={gemini_key}\n")
    f.write(f"DISCORD_BOT_TOKEN={discord_token}\n")
    f.write(f"DISCORD_ALLOWED_USERS={allowed_users}\n")
    f.write(f"GATEWAY_ALLOWED_USERS={allowed_users}\n")
    f.write("GATEWAY_ALLOW_ALL_USERS=true\n")
    f.write("DISCORD_AUTO_THREAD=false\n")

# 4. Export for subprocess
os.environ["OPENAI_API_KEY"] = gemini_key
os.environ["GEMINI_API_KEY"] = gemini_key
os.environ["GOOGLE_API_KEY"] = gemini_key
os.environ["DISCORD_BOT_TOKEN"] = discord_token
os.environ["DISCORD_ALLOWED_USERS"] = allowed_users
os.environ["GATEWAY_ALLOWED_USERS"] = allowed_users
os.environ["GATEWAY_ALLOW_ALL_USERS"] = "true"
os.environ["DISCORD_AUTO_THREAD"] = "false"

# 5. Lightweight HTTP Health Check on Port 7860 (Hugging Face / Render)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """<!DOCTYPE html>
<html>
<head><title>Hermes Agent</title><style>body{font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}div{text-align:center;background:#1e293b;padding:2rem;border-radius:1rem;box-shadow:0 10px 25px rgba(0,0,0,0.5);}h1{color:#38bdf8;margin:0 0 1rem;}</style></head>
<body>
<div>
<h1>🤖 Hermes Agent Discord Gateway</h1>
<p style="font-size:1.2rem;color:#4ade80;">🟢 Status: Online 24/7 (2 Dedicated vCPUs · 16 GB RAM)</p>
<p style="color:#94a3b8;">Listening to Discord mentions & direct messages.</p>
</div>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 7860))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[Health Server] Listening on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()
    print("[Hermes Gateway] Starting Discord Gateway daemon...")
    subprocess.run(["hermes", "gateway", "run"])
