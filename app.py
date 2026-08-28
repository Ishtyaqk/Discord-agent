import os
import shutil
import subprocess
import threading
import traceback
import gradio as gr

# 1. Setup Hermes configuration directory
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

# Copy custom SOUL.md if present
if os.path.exists("SOUL.md"):
    with open("SOUL.md", "r", encoding="utf-8") as src, open(os.path.join(hermes_dir, "SOUL.md"), "w", encoding="utf-8") as dst:
        dst.write(src.read())

# Copy Agent Reach skills if present
if os.path.exists("skills"):
    dest_skills = os.path.join(hermes_dir, "skills")
    if os.path.exists(dest_skills):
        shutil.rmtree(dest_skills)
    shutil.copytree("skills", dest_skills)

# 2. Automated bootstrap: Use uv to install Python 3.11 & Hermes runtime in user space
def start_hermes_daemon():
    try:
        print("[Hermes Setup] Setting up isolated Python 3.11 environment via uv...")
        uv_bin = os.path.expanduser("~/.local/bin/uv")
        if not os.path.exists(uv_bin):
            subprocess.run("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True, check=True)

        venv_dir = os.path.expanduser("~/hermes_venv")
        if not os.path.exists(venv_dir):
            subprocess.run(f"{uv_bin} venv --python 3.11 {venv_dir}", shell=True, check=True)
            print("[Hermes Setup] Installing hermes-agent via uv...")
            subprocess.run(
                f"{uv_bin} pip install --python {venv_dir}/bin/python git+https://github.com/NousResearch/hermes-agent.git",
                shell=True,
                check=True,
            )

        print("[Hermes Gateway] Starting Discord Gateway daemon on 2 vCPU hardware...")
        hermes_bin = f"{venv_dir}/bin/hermes"
        env = os.environ.copy()
        env["DISCORD_BOT_TOKEN"] = discord_token
        env["DISCORD_ALLOWED_USERS"] = allowed_users
        env["GATEWAY_ALLOW_ALL_USERS"] = "true"
        env["DISCORD_AUTO_THREAD"] = "false"
        env["OPENAI_API_KEY"] = gemini_key
        env["GEMINI_API_KEY"] = gemini_key
        subprocess.run([hermes_bin, "gateway", "run"], env=env)
    except Exception as e:
        print(f"[Hermes Gateway Error] {e}")
        traceback.print_exc()

threading.Thread(target=start_hermes_daemon, daemon=True).start()

# 3. Live Gradio Web Status Page
with gr.Blocks(title="Hermes Agent Discord Bot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Hermes Agent — Discord Gateway")
    gr.Markdown("🟢 **Status:** Active & Online 24/7 on **2 Dedicated vCPUs · 16 GB RAM**.")
    gr.Markdown("You can send messages and `@mentions` directly in your Discord server!")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr=False)
