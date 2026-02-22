import os
import requests
import time
import base64
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GH_TOKEN = os.environ.get("GH_TOKEN")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0.7
)

def get_github_file(repo, path):
    url = f"https://api.github.com/repos/trinity6official/{repo}/contents/{path}"
    headers = {}
    if GH_TOKEN:
        headers["Authorization"] = f"token {GH_TOKEN}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")
    return None

def get_repo_structure(repo):
    url = f"https://api.github.com/repos/trinity6official/{repo}/git/trees/main?recursive=1"
    headers = {}
    if GH_TOKEN:
        headers["Authorization"] = f"token {GH_TOKEN}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tree = response.json().get("tree", [])
        files = [item["path"] for item in tree if item["type"] == "blob"]
        return "\n".join(files)
    return None

def build_context():
    context = "TRINITY6 PROJECT CONTEXT\n\n"

    scanner_readme = get_github_file("Trinity6", "README.md")
    if scanner_readme:
        context += "TRINITY6 SCANNER README:\n"
        context += scanner_readme[:2000]
        context += "\n\n"

    scanner_structure = get_repo_structure("Trinity6")
    if scanner_structure:
        context += "TRINITY6 SCANNER FILES:\n"
        context += scanner_structure
        context += "\n\n"

    assistant_structure = get_repo_structure("assistant")
    if assistant_structure:
        context += "TRINITY6 ASSISTANT FILES:\n"
        context += assistant_structure
        context += "\n\n"

    return context

def ask_claude(question, context):
    system_prompt = f"""You are Trinity6 AI Assistant,
the personal AI for David, founder of Trinity6.

{context}

DAVID'S BACKGROUND:
Works in GRC compliance professionally.
Knows Python and Ruby.
Building Trinity6 as his own cybersecurity company.
Hardware with RTX 4060 GPU arriving soon.
Based in India. Works on Trinity6 in his spare time.

YOUR ROLE:
Help David with anything related to Trinity6.
Answer questions about his project progress.
Write code when asked.
Plan next steps based on roadmap.
Answer cybersecurity and GRC questions.
Write LinkedIn posts and YouTube scripts.
Advise on product and business decisions.

Keep responses concise and practical.
No markdown stars or symbols.
Plain text only.
Be direct and helpful."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    return response.content

def send_message(text, chat_id):
    url = f"{BASE_URL}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        payload = {"chat_id": chat_id, "text": chunk}
        requests.post(url, json=payload)
        time.sleep(0.5)

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return {"ok": False}

def handle_message(text, chat_id, context):
    text = text.strip()

    if text == "/start" or text == "/help":
        send_message("""Trinity6 AI Assistant is online.

I have read your Trinity6 repositories and know your project.

Ask me anything:
- What have I built so far?
- What is next in my roadmap?
- Write code for Phase 2
- Explain my scanner architecture
- Write a LinkedIn post about zero trust
- What should I work on this weekend?

Commands:
/help - Show this menu
/progress - Your project status
/next - What to build next
/status - System status""", chat_id)

    elif text == "/progress":
        send_message("Reading your repositories...", chat_id)
        response = ask_claude(
            "Summarize David's current progress on Trinity6 based on the repository files. What has been built and what is remaining.",
            context
        )
        send_message(response, chat_id)

    elif text == "/next":
        send_message("Checking your roadmap...", chat_id)
        response = ask_claude(
            "Based on Trinity6 repository and roadmap what should David work on next? Be specific.",
            context
        )
        send_message(response, chat_id)

    elif text == "/status":
        send_message("""Trinity6 System Status

AI Assistant: Online
Website: trinity6.com - Live
Scanner: Phase 1 Complete
Daily Reports: 9:30 AM IST
GitHub: trinity6official

Send /progress for detailed project status.""", chat_id)

    else:
        send_message("Thinking...", chat_id)
        try:
            response = ask_claude(text, context)
            send_message(response, chat_id)
        except Exception as e:
            send_message(f"Error: {str(e)}", chat_id)

def main():
    print("Trinity6 Bot starting...")
    print("Reading repositories...")

    context = build_context()
    print("Repository context loaded!")

    send_message(
        "Trinity6 AI Assistant is online. I have read your repositories and know your project. Send /help for commands or ask me anything.",
        TELEGRAM_CHAT_ID
    )

    offset = None
    context_refresh = 0

    while True:
        try:
            updates = get_updates(offset)

            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1

                    message = update.get("message", {})
                    text = message.get("text", "")
                    chat_id = str(message.get("chat", {}).get("id", ""))

                    if text and chat_id:
                        print(f"Received: {text}")
                        handle_message(text, chat_id, context)

            context_refresh += 1
            if context_refresh >= 60:
                print("Refreshing repository context...")
                context = build_context()
                context_refresh = 0

            time.sleep(1)

        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()
