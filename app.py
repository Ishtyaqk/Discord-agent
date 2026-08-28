import os
import shutil
import subprocess
import threading
import gradio as gr

# 1. Setup Hermes configuration directory in Hugging Face user home
hermes_dir = os.path.expanduser("~/.hermes")
os.makedirs(hermes_dir, exist_ok=True)

gemini_key = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("GOOGLE_API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or ""
).strip()

discord_token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
allowed_users = os.environ.get("DISCORD_ALLOWED_USERS", "*").strip()

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

# Copy custom SOUL.md persona if present
if os.path.exists("SOUL.md"):
    with open("SOUL.md", "r", encoding="utf-8") as src, open(os.path.join(hermes_dir, "SOUL.md"), "w", encoding="utf-8") as dst:
        dst.write(src.read())

# Copy Agent Reach skills if present
if os.path.exists("skills"):
    dest_skills = os.path.join(hermes_dir, "skills")
    if os.path.exists(dest_skills):
        shutil.rmtree(dest_skills)
    shutil.copytree("skills", dest_skills)

# 2. Launch Hermes Gateway in background thread on Hugging Face 2 vCPU hardware
def start_hermes_daemon():
    print("[Hermes Gateway] Starting on Hugging Face 2 vCPU environment...")
    os.environ["DISCORD_BOT_TOKEN"] = discord_token
    os.environ["DISCORD_ALLOWED_USERS"] = allowed_users
    os.environ["GATEWAY_ALLOW_ALL_USERS"] = "true"
    os.environ["DISCORD_AUTO_THREAD"] = "false"
    os.environ["OPENAI_API_KEY"] = gemini_key
    os.environ["GEMINI_API_KEY"] = gemini_key
    subprocess.run(["hermes", "gateway", "run"])

t = threading.Thread(target=start_hermes_daemon, daemon=True)
t.start()

# 3. Live Gradio Web Status Page
with gr.Blocks(title="Hermes Agent Discord Bot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Hermes Agent — Discord Gateway")
    gr.Markdown("🟢 **Status:** Active & Online 24/7 on **2 Dedicated vCPUs · 16 GB RAM**.")
    gr.Markdown("You can send messages and `@mentions` directly in your Discord server!")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
