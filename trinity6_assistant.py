import os
import requests
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0.7
)

# ============================================
# AGENTS
# ============================================

research_agent = Agent(
    role="Technology Research Specialist",
    goal="""Research latest news and insights across 
    cybersecurity, GRC compliance, artificial 
    intelligence, and technology trends.""",
    backstory="""You are an expert researcher with 
    deep knowledge across cybersecurity, GRC 
    frameworks, AI developments, and emerging 
    technology trends. You work for Trinity6, an 
    AI powered cybersecurity company.""",
    llm=llm,
    verbose=True
)

content_agent = Agent(
    role="LinkedIn Content Strategist",
    goal="""Draft one engaging LinkedIn post about 
    cybersecurity, GRC compliance, AI, or technology 
    for Trinity6.""",
    backstory="""You are a skilled content writer 
    specializing in cybersecurity and technology 
    content for professional audiences on LinkedIn.""",
    llm=llm,
    verbose=True
)

shorts_agent = Agent(
    role="YouTube Shorts Creator",
    goal="""Create one viral YouTube Shorts script 
    about cybersecurity, GRC, AI, or technology 
    for Trinity6 channel.""",
    backstory="""You are an expert at creating viral 
    short form video content that educates technology 
    professionals in 60 seconds or less.""",
    llm=llm,
    verbose=True
)

# ============================================
# TASKS
# ============================================

research_task = Task(
    description="""Research the latest updates across 
    these four areas today:
    
    1. Cybersecurity - latest threats or incidents
    2. GRC Compliance - CIS, NIST, ISO 27001 updates
    3. Artificial Intelligence - latest developments
    4. Technology - emerging trends
    
    Return ONLY a clean structured report.
    No markdown symbols. No stars. No hashtags.
    Use plain text only.
    
    Format exactly like this:
    
    CYBERSECURITY
    [One paragraph about latest cybersecurity insight]
    
    GRC COMPLIANCE
    [One paragraph about latest GRC insight]
    
    ARTIFICIAL INTELLIGENCE
    [One paragraph about latest AI insight]
    
    TECHNOLOGY
    [One paragraph about latest technology insight]""",
    expected_output="""Clean plain text report with 
    four sections. No markdown. No stars. No symbols.""",
    agent=research_agent
)

content_task = Task(
    description="""Using the research provided write 
    one LinkedIn post for Trinity6.
    
    Requirements:
    - Under 200 words
    - Strong opening line
    - Professional but conversational tone
    - End with one question to drive engagement
    - Add 5 hashtags on the last line
    
    Return ONLY the LinkedIn post text.
    No introduction. No explanation.
    No markdown symbols. No stars.
    Just the post exactly as it would appear on LinkedIn.
    Start directly with the first line of the post.""",
    expected_output="""Ready to publish LinkedIn post 
    in plain text. No markdown. No stars. No symbols. 
    Just the post content and hashtags.""",
    agent=content_agent
)

shorts_task = Task(
    description="""Using the research provided create 
    one YouTube Shorts script for Trinity6.
    
    Requirements:
    - Maximum 60 seconds when read aloud
    - Powerful hook in first 3 seconds
    - Visual directions in brackets like [show screen]
    - End with call to action to follow Trinity6
    - Include suggested title
    - Include 5 hashtags
    
    Return ONLY the script.
    No introduction. No explanation.
    No markdown symbols. No stars.
    Format exactly like this:
    
    TITLE
    [Your suggested title here]
    
    HOOK
    [First 3 seconds script]
    
    SCRIPT
    [Full script with visual directions]
    
    HASHTAGS
    [5 hashtags]""",
    expected_output="""Complete YouTube Shorts script 
    in plain text. No markdown. No stars.""",
    agent=shorts_agent
)

# ============================================
# TELEGRAM FUNCTION
# ============================================

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed: {response.json()}")

# ============================================
# RUN CREW
# ============================================

crew = Crew(
    agents=[research_agent, content_agent, shorts_agent],
    tasks=[research_task, content_task, shorts_task],
    process=Process.sequential,
    verbose=True
)

print("Starting Trinity6 AI Agents...")

results = crew.kickoff(return_tasks_output=True)

research_output = str(research_task.output)
linkedin_output = str(content_task.output)
shorts_output = str(shorts_task.output)

# ============================================
# SEND TO TELEGRAM
# ============================================

# Message 1 - Research
message1 = f"""<b>Trinity6 Daily Intelligence Report</b>
<b>Cybersecurity · GRC · AI · Technology</b>

<b>Research Insights</b>

{research_output[:3500]}"""

# Message 2 - LinkedIn Post
message2 = f"""<b>LinkedIn Post</b>

{linkedin_output[:3500]}"""

# Message 3 - YouTube Shorts
message3 = f"""<b>YouTube Shorts Script</b>

{shorts_output[:3500]}

Trinity6 AI Assistant
trinity6.com"""

send_to_telegram(message1)
send_to_telegram(message2)
send_to_telegram(message3)

print("All messages sent!")
print("\n=== DONE ===")
