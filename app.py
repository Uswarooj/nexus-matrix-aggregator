import streamlit as st
import feedparser
import sqlite3
import json
import os
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# ==========================================
# 1. Configuration & Setup
# ==========================================
load_dotenv()

# Using Gemini API to completely fix the 429 OpenAI Billing Error
API_KEY = os.getenv("GEMINI_API_KEY")
try:
    if not API_KEY:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if API_KEY:
    genai.configure(api_key=API_KEY)

DB_NAME = "leads_v2.db"
RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.zdnet.com/news/rss.xml"
]

# ==========================================
# 2. Database Core Logic
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            link TEXT PRIMARY KEY,
            title TEXT,
            published TEXT,
            insight TEXT,
            added_on TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_lead(link, title, published, insight):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO leads (link, title, published, insight, added_on)
            VALUES (?, ?, ?, ?, ?)
        ''', (link, title, published, insight, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  
    conn.close()

def get_all_leads():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT title, link, published, insight, added_on FROM leads ORDER BY added_on DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def lead_exists(link):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT 1 FROM leads WHERE link = ?', (link,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# ==========================================
# 3. Gemini Free AI Engine Pipeline
# ==========================================
def analyze_article(title, summary):
    if not API_KEY:
        return False, "API Key Missing"
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an expert B2B Lead Generation Analyst. Analyze this news:
    Headline: {title}
    Summary: {summary}

    Check if this organization is experiencing:
    1. Critical technical failure, data breach, system outage, or cyber attack.
    2. Operational bottleneck or legacy system issues.
    3. Direct need for AI or workflow automation.
    
    Respond STRICTLY in this JSON format:
    {{
        "is_lead": true/false,
        "insight": "A short 1-sentence explanation of the business problem or why they need tech solutions."
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
        return result.get("is_lead", False), result.get("insight", "")
    except Exception as e:
        return False, f"AI Error: {str(e)}"
# ==========================================
# 4. Stream Sync Ingestion (TESTING VERSION)
# ==========================================
def fetch_and_process_news(limit_per_feed=8):
    new_leads_found = 0
    status_box = st.empty()
    
    for feed_url in RSS_FEEDS:
        status_box.markdown(f"📡 *Scanning updates from:* `{feed_url}`")
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:limit_per_feed]:
            if lead_exists(entry.link):
                continue
            
            title = entry.title
            summary = entry.get('summary', '')[:500]
            published = entry.get('published', 'Recent')
            
            is_lead, insight = analyze_article(title, summary)
        
            save_lead(entry.link, title, published, insight)
            new_leads_found += 1
                
    status_box.empty()
    return new_leads_found


# ==========================================
# 5. UI Custom Styling & Rendering
# ==========================================
st.set_page_config(page_title="NexusAI | Core Matrix", page_icon="🔮", layout="wide")
init_db()

# Premium Cyberpunk & Dynamic Imagery CSS Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap');
    
    /* Global Background with Abstract Dark Tech Overlay */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-image: linear-gradient(rgba(8, 7, 16, 0.92), rgba(8, 7, 16, 0.95)), 
                          url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #e2e8f0;
    }
    
    /* Header Container with Dynamic Image Banner Background */
    .premium-hero {
        position: relative;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(49, 16, 66, 0.85) 50%, rgba(8, 7, 16, 0.9) 100%),
                    url('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 24px;
        padding: 60px;
        margin-bottom: 40px;
        text-align: center;
        box-shadow: 0 20px 50px rgba(124, 58, 237, 0.15);
        overflow: hidden;
    }
    
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #f43f5e, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
        letter-spacing: 2px;
        filter: drop-shadow(0 2px 10px rgba(167, 139, 250, 0.3));
    }

    /* Glowing Glassmorphism KPI Display Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.15) !important;
        transform: translateY(-5px);
    }

    /* Advanced Cyberpunk Lead Cards */
    .cyber-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-left: 6px solid #f43f5e;
        border-radius: 20px;
        padding: 35px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .cyber-card:hover {
        border-left: 6px solid #38bdf8;
        background: rgba(15, 23, 42, 0.65);
        box-shadow: 0 20px 40px rgba(56, 189, 248, 0.08);
        transform: scale(1.01);
    }

    .card-badge {
        background: linear-gradient(90deg, #f43f5e, #e11d48);
        color: white;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        display: inline-block;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(244, 63, 94, 0.3);
    }
    
    .insight-zone {
        background: rgba(56, 189, 248, 0.04);
        border: 1px dashed rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 20px;
        margin: 22px 0;
    }

    /* Input Fields & Buttons styling alignment */
    .stButton>button {
        background: linear-gradient(90deg, #7c3aed, #f43f5e) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.25) !important;
    }
    .stButton>button:hover {
        box-shadow: 0 6px 25px rgba(244, 63, 94, 0.4) !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# ===== HERO PRESENTATION WITH GRAPHICS =====
st.markdown("""
    <div class="premium-hero">
        <div class="hero-title">🔮 NEXUS MATRIX AGGREGATOR</div>
        <p style="color: #cbd5e1; font-size: 1.25rem; max-width: 850px; margin: 0 auto; font-weight: 300; line-height: 1.6;">
            Autonomous AI architecture scanning decentralized web streams. Instantly intercepting corporate network vulnerabilities, legacy technical blockages, and high-intent B2B integration vectors.
        </p>
    </div>
""", unsafe_allow_html=True)


# System Stats
stored_leads = get_all_leads()

# ===== INTERACTIVE METRIC GRAPHICS =====
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🎯 Total Target Leads Logged", value=len(stored_leads))
with col2:
    st.metric(label="📡 Connected Feed Transmitters", value=len(RSS_FEEDS))
with col3:
    st.metric(label="⚡ Intelligent Engine Status", value="Gemini 1.5 Free Mode")

st.markdown("<br>", unsafe_allow_html=True)

# ===== CONTROL SIDEBAR =====
with st.sidebar:
    st.markdown("### 🛠️ Core Control Panel")
    st.write("Trigger secure global crawling data streams via autonomous prompts.")
    st.divider()
    
    if not API_KEY:
        st.error("🔒 GEMINI_API_KEY Missing! Paste it into your .env file.")
    else:
        st.success("⚡ Gemini Neural Grid Linked")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🛰️ LAUNCH DYNAMIC CRAWL", type="primary", use_container_width=True, disabled=not API_KEY):
        with st.spinner("Synchronizing data nodes..."):
            count = fetch_and_process_news()
            st.toast(f"Matrix updated successfully! Discovered {count} critical leads.", icon="💥")
            st.rerun()

# ===== MAIN APPLICATION STREAM =====
st.markdown("### 📋 Actionable Targets Live Intelligence Feed")

if not stored_leads:
    st.markdown("""
        <div style="text-align: center; padding: 80px; background: rgba(255,255,255,0.02); border-radius: 20px; border: 2px dashed rgba(255,255,255,0.1);">
            <h4 style="color: #64748b; margin: 0;">No active targets recorded inside local database sequence.</h4>
            <p style="color: #475569; margin-top: 8px; margin-bottom: 0;">Click 'LAUNCH DYNAMIC CRAWL' inside the sidebar node to initialize processing.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    for title, link, published, insight, added_on in stored_leads:
        st.markdown(f"""
            <div class="cyber-card">
                <div class="card-badge">🔥 Automation Intent Found</div>
                <h3 style="color: #ffffff; margin-top: 0; font-size: 1.4rem; font-weight: 700;">{title}</h3>
                <div style="display: flex; gap: 25px; color: #64748b; font-size: 0.85rem; margin-bottom: 10px;">
                    <span>📅 <b>Published:</b> {published}</span>
                    <span>⏱️ <b>Ingested:</b> {added_on[:16].replace('T', ' ')}</span>
                </div>
                <div class="insight-zone">
                    <span style="color: #a78bfa; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; display: block; margin-bottom: 5px; letter-spacing: 0.5px;">💡 LLM Core Assessment:</span>
                    <span style="color: #cbd5e1; font-size: 1rem; font-style: italic;">"{insight}"</span>
                </div>
                <a href="{link}" target="_blank" style="text-decoration: none; display: inline-block; background: linear-gradient(90deg, #7c3aed, #4c1d95); color: white; padding: 10px 22px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);">
                    Analyze Source Signal →
                </a>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
st.caption("🔮 System Grid Engine: Streamlit V2 + Gemini Pro Model Configuration Matrix")