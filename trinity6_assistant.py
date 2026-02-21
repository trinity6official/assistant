import os
import requests
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic

# API Keys from environment variables
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

# Language Model
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
    intelligence, and technology trends. Find the 
    most interesting and relevant updates that 
    professionals need to know today.""",
    backstory="""You are an expert researcher with 
    deep knowledge across cybersecurity, GRC 
    frameworks, AI developments, and emerging 
    technology trends. You work for Trinity6, an 
    AI powered cybersecurity company. You find 
    the most compelling and relevant insights 
    that educate and engage technology 
    professionals.""",
    llm=llm,
    verbose=True
)

content_agent = Agent(
    role="Content Strategist",
    goal="""Draft engaging LinkedIn posts about 
    cybersecurity, GRC compliance, AI, and 
    technology for Trinity6. Create content 
    that builds Trinity6 as a thought leader 
    across all these domains.""",
    backstory="""You are a skilled content writer 
    specializing in cybersecurity, AI, and 
    technology content for professional audiences. 
    You create content that attracts potential 
    clients and builds Trinity6 as the go-to 
    company for AI powered cybersecurity.""",
    llm=llm,
    verbose=True
)

shorts_agent = Agent(
    role="YouTube Shorts Content Creator",
    goal="""Create viral engaging YouTube Shorts 
    scripts about cybersecurity, GRC compliance, 
    AI, and technology for Trinity6 channel.""",
    backstory="""You are an expert at creating 
    viral short form video content that educates 
    and entertains technology professionals. 
    You know exactly how to hook viewers in 
    the first 3 seconds and deliver maximum 
    value in 60 seconds. You create content 
    for Trinity6, an AI powered cybersecurity 
    company building authority in cybersecurity, 
    GRC, AI, and technology space.""",
    llm=llm,
    verbose=True
)

# ============================================
# TASKS
# ============================================

research_task = Task(
    description="""Research the latest updates across 
    these four areas today:
    
    1. Cybersecurity - latest threats, vulnerabilities, 
    or security incidents
    2. GRC Compliance - CIS, NIST, ISO 27001 updates 
    or compliance trends
    3. Artificial Intelligence - latest AI developments, 
    tools, or breakthroughs
    4. Technology - emerging tech trends affecting 
    businesses and security
    
    Find the top most interesting and relevant 
    insight from each area. Focus on practical 
    information that business professionals 
    and cybersecurity engineers would find 
    valuable and interesting.""",
    expected_output="""A structured report with 
    one key insight from each of the four areas - 
    Cybersecurity, GRC, AI, and Technology. 
    Each insight should include what happened, 
    why it matters, and practical implications.""",
    agent=research_agent
)

content_task = Task(
    description="""Using the research provided, 
    draft one professional engaging LinkedIn post 
    for Trinity6. 
    
    Choose the most compelling insight from 
    the research across cybersecurity, GRC, 
    AI, or technology. Mix topics across 
    different days to keep content varied 
    and interesting.
    
    Post requirements:
    - Under 200 words
    - Strong opening line that stops scrolling
    - Valuable insight or tip
    - Position Trinity6 as intelligent expert
    - Professional but conversational tone
    - End with a thought provoking question
      to drive engagement
    - Include 5 relevant hashtags""",
    expected_output="""A ready to publish LinkedIn 
    post that is professional, engaging, positions 
    Trinity6 as cybersecurity and AI expert, 
    under 200 words with hashtags.""",
    agent=content_agent
)

shorts_task = Task(
    description="""Using the research provided, 
    create one highly engaging YouTube Shorts 
    script for Trinity6. 
    
    Choose the single most interesting insight 
    from the research - could be from cybersecurity, 
    GRC, AI, or technology. Pick whichever is 
    most surprising, alarming, or fascinating.
    
    Script requirements:
    - Maximum 60 seconds when read aloud
    - First 3 seconds must have a powerful hook 
      that stops scrolling
    - Deliver one clear valuable insight
    - Include one practical tip or action
    - End with call to action to follow Trinity6
    - Include visual directions in brackets 
      like [show hacker screen] or [show AI visual]
    - Conversational and energetic tone
    - No corporate jargon""",
    expected_output="""A complete YouTube Shorts 
    script including:
    - Hook line for first 3 seconds
    - Main content with visual directions
    - Practical tip
    - Call to action
    - Estimated read time
    - Suggested title for the Short
    - 5 relevant hashtags""",
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
        print("Message sent to Telegram successfully!")
    else:
        print("Failed to send message")
        print(response.json())

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
result = crew.kickoff()

# ============================================
# SEND TO TELEGRAM
# ============================================

# Split output into sections
output_text = str(result)

# Message 1 - Header and Research
message1 = f"""
<b>🛡️ Trinity6 Daily Content Report</b>
<b>📊 Cybersecurity · GRC · AI · Technology</b>

<b>📰 Research Insights</b>
{output_text[:1000]}
"""

# Message 2 - LinkedIn Post
message2 = f"""
<b>💼 LinkedIn Post - Ready to Publish</b>

{output_text[1000:2500]}
"""

# Message 3 - YouTube Shorts Script
message3 = f"""
<b>🎬 YouTube Shorts Script - Ready to Film</b>

{output_text[2500:4000]}

<i>✅ Generated by Trinity6 AI Assistant</i>
<i>🌐 trinity6.com</i>
"""

# Send three separate messages
send_to_telegram(message1)
send_to_telegram(message2)
send_to_telegram(message3)

print("\n=== FINAL OUTPUT ===")
print(result)
