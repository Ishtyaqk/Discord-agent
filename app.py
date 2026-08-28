import os
import shutil
import subprocess
import threading
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

discord_token = (os.environ.get("DISCORD_BOT_TOKEN") or "").strip()
allowed_users = (os.environ.get("DISCORD_ALLOWED_USERS") or "*").strip()

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

# 2. Automated background thread to initialize Python 3.11 runtime & run Hermes Gateway
def run_hermes_bot():
    try:
        print("[Hermes Setup] Preparing Python 3.11 runtime via uv...")
        venv_dir = os.path.expanduser("~/hermes_venv")
        if not os.path.exists(venv_dir):
            subprocess.run(f"uv venv --python 3.11 {venv_dir}", shell=True, check=True)
            print("[Hermes Setup] Installing hermes-agent engine...")
            subprocess.run(
                f"uv pip install --python {venv_dir}/bin/python git+https://github.com/NousResearch/hermes-agent.git yt-dlp",
                shell=True,
                check=True,
            )

        print("[Hermes Gateway] Starting Discord Gateway daemon...")
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

threading.Thread(target=run_hermes_bot, daemon=True).start()

# 3. Clean Gradio UI
with gr.Blocks(title="Hermes Agent Discord Gateway") as demo:
    gr.Markdown("# 🤖 Hermes Agent — Discord Gateway")
    gr.Markdown("🟢 **Status:** Active & Online 24/7.")
    gr.Markdown("Send `@mentions` or Direct Messages to your bot in Discord!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
