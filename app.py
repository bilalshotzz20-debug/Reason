import streamlit as st
import os
import sqlite3
import re
import datetime
import pypdf
from groq import Groq
from fpdf import FPDF

# ==========================================
# 1. PAGE CONFIG & SETUP
# ==========================================
st.set_page_config(page_title="Reason | Your Health Solution", page_icon="🫀", layout="wide", initial_sidebar_state="expanded")

# Database Init
def init_db():
    conn = sqlite3.connect('reason_health.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS profile 
                 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, gender TEXT, height REAL, weight REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS health_records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, symptoms TEXT, analysis TEXT)''')
    conn.commit()
    conn.close()

init_db()

def load_profile():
    conn = sqlite3.connect('reason_health.db')
    c = conn.cursor()
    c.execute("SELECT * FROM profile WHERE id=1")
    row = c.fetchone()
    conn.close()
    if row:
        return {"name": row[1], "age": row[2], "gender": row[3], "height": row[4], "weight": row[5]}
    return {"name": "", "age": 25, "gender": "Male", "height": 170.0, "weight": 70.0}

if "profile" not in st.session_state:
    st.session_state.profile = load_profile()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Reason. I am here to help you understand your health better. How are you feeling today?"}
    ]

if "report_data" not in st.session_state:
    st.session_state.report_data = None

try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = ""

# ==========================================
# 2. ANIMATED PREMIUM CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #F8FAFC !important; color: #1E293B !important; overflow-x: hidden; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 1300px !important; padding-top: 2rem; padding-bottom: 5rem; }
h1, h2, h3, h4, h5, h6, p, span, div, li, label { color: #1E293B !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; padding-top: 20px;}
[data-testid="stSidebar"] * { color: #1E293B !important; }
.sidebar-logo { font-size: 1.8rem; font-weight: 800; color: #0EA5E9 !important; margin-bottom: 10px;}
.sidebar-sub { font-size: 0.85rem; color: #64748B !important; margin-bottom: 25px;}

/* ANIMATED CHAT BUBBLES */
.chat-bubble-user { 
    background-color: #0EA5E9; color: white !important; padding: 15px 20px; 
    border-radius: 20px 20px 0 20px; margin-bottom: 15px; margin-left: 15%; font-size: 0.95rem; 
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.2);
    animation: slideUp 0.4s ease-out forwards;
}
.chat-bubble-ai { 
    background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 20px; 
    border-radius: 20px 20px 20px 0; margin-bottom: 15px; margin-right: 15%; font-size: 0.95rem; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    animation: slideUp 0.4s ease-out forwards;
}
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* FILE UPLOADER */
[data-testid="stFileUploadDropzone"] { background-color: #F1F5F9 !important; border: 2px dashed #94A3B8 !important; border-radius: 12px !important; padding: 20px !important; }
[data-testid="stFileUploadDropzone"] * { color: #475569 !important; }

/* REPORT PANEL */
.report-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); animation: fadeIn 0.6s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.report-title { font-size: 1.4rem; font-weight: 800; color: #0EA5E9 !important; margin-bottom: 15px;}
.report-content h3 { font-size: 1.1rem !important; color: #0F172A !important; margin-top: 20px; border-bottom: 2px solid #F1F5F9; padding-bottom: 5px;}
.report-content p, .report-content li { font-size: 0.95rem !important; color: #334155 !important; line-height: 1.6;}

/* BUTTONS */
.stButton > button { background-color: #0EA5E9 !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 700 !important; padding: 10px 20px; border: none !important; width: 100%; transition: 0.3s;}
.stButton > button:hover { background-color: #0284C7 !important; transform: scale(1.02); }
.stDownloadButton > button { background-color: #10B981 !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 700 !important; border: none !important; width: 100%; transition: 0.3s;}
.stDownloadButton > button:hover { transform: scale(1.02); }

/* CHAT INPUT */
[data-testid="stChatInput"] > div { background-color: #FFFFFF !important; border: 2px solid #E2E8F0 !important; border-radius: 30px !important; padding: 8px 20px !important; }
[data-testid="stChatInput"] textarea { color: #1E293B !important; }

/* ANIMATED HEARTBEAT LOADER */
.heartbeat-loader {
    display: flex; justify-content: center; align-items: center; gap: 10px; margin: 20px 0;
}
.heartbeat-loader svg {
    width: 40px; height: 40px; fill: #EF4444; 
    animation: heartbeat 1.2s infinite;
}
.heartbeat-loader span { color: #64748B; font-weight: 600; font-size: 0.9rem;}
@keyframes heartbeat {
    0% { transform: scale(1); }
    14% { transform: scale(1.3); }
    28% { transform: scale(1); }
    42% { transform: scale(1.3); }
    70% { transform: scale(1); }
}

/* ANIMATED HEALTH SCORE BAR */
.score-container { margin-bottom: 20px; }
.score-label { display: flex; justify-content: space-between; font-weight: 700; font-size: 0.9rem; margin-bottom: 5px; }
.score-bar-bg { width: 100%; height: 12px; background-color: #E2E8F0; border-radius: 10px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, #EF4444, #F59E0B, #10B981); width: 0%; transition: width 1.5s ease-in-out; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPERS & PROMPTS
# ==========================================
def extract_text_from_pdfs(pdf_files):
    text = ""
    for pdf in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except:
            pass
    return text

def parse_health_score(analysis_text):
    # AI se score extract karne ki koshish (Regex)
    match = re.search(r'Score:\s*(\d+)', analysis_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 85 # Default fallback

# ==========================================
# 4. SIDEBAR (PROFILE)
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🫀 Reason</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Your Personal Health Solution</div>', unsafe_allow_html=True)
    
    st.markdown("### 👤 My Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.profile['name'])
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 1, 120, value=st.session_state.profile['age'])
            height = st.number_input("Height (cm)", 50.0, 250.0, value=st.session_state.profile['height'])
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.profile['gender']))
            weight = st.number_input("Weight (kg)", 10.0, 300.0, value=st.session_state.profile['weight'])
        
        if st.form_submit_button("Update Profile"):
            conn = sqlite3.connect('reason_health.db')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO profile (id, name, age, gender, height, weight) VALUES (1, ?, ?, ?, ?, ?)", (name, age, gender, height, weight))
            conn.commit()
            conn.close()
            st.session_state.profile = {"name": name, "age": age, "gender": gender, "height": height, "weight": weight}
            st.success("Profile Updated!")

    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    api_key_input = SECRET_KEY if SECRET_KEY else st.text_input("API Key", type="password")

# ==========================================
# 5. MAIN UI (2 COLUMNS)
# ==========================================
col_chat, col_report = st.columns([1.2, 1], gap="large")

with col_chat:
    st.markdown(f"### Welcome back, {st.session_state.profile['name'] if st.session_state.profile['name'] else 'Friend'}! 👋")
    st.markdown("<p style='color: #64748B;'>Let's understand your health together. You can type your symptoms or upload a lab report.</p>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            
    st.markdown("#### 📄 Have a Lab Report?")
    uploaded_files = st.file_uploader("Upload Lab Reports (PDF)", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files and st.button("Explain My Reports"):
        if not api_key_input:
            st.error("API Key missing.")
        else:
            # Show Animated Heartbeat Loader
            loader_placeholder = st.empty()
            loader_placeholder.markdown("""
            <div class="heartbeat-loader">
                <svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                <span>Reason is analyzing your reports...</span>
            </div>
            """, unsafe_allow_html=True)

            extracted_text = extract_text_from_pdfs(uploaded_files)
            
            sys_prompt = f"""
            You are Reason, a compassionate health guide.
            Patient: {st.session_state.profile['age']}y, {st.session_state.profile['gender']}, Weight: {st.session_state.profile['weight']}kg.
            
            Explain this lab report in simple English.
            
            FORMAT STRICTLY LIKE THIS:
            Health Score: [Number between 10 and 100]
            
            ### 📊 What Your Report Says
            [Simple explanation]
            
            ### 🩺 Possible Reasons
            [2-3 simple reasons]
            
            ### 💡 Next Steps
            *   **Diet:** [Food advice]
            *   **Doctor:** [Which specialist to visit]
            """
            
            client = Groq(api_key=api_key_input)
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": extracted_text}],
                model="openai/gpt-oss-120b", temperature=0.3
            ).choices[0].message.content
            
            loader_placeholder.empty() # Remove loader
            st.session_state.report_data = res
            st.session_state.messages.append({"role": "user", "content": f"Uploaded {len(uploaded_files)} lab report(s)."})
            st.session_state.messages.append({"role": "assistant", "content": "Analysis complete! I have created your Health Insights on the right."})
            st.rerun()

with col_report:
    if st.session_state.report_data:
        # Extract Score
        score = parse_health_score(st.session_state.report_data)
        
        # Clean text for display
        clean_text = re.sub(r'Health Score:\s*\d+', '', st.session_state.report_data)
        formatted_report = clean_text.replace('###', '<h3>').replace('**', '').replace('\n', '<br>')
        
        # Animated Score Bar Color
        bar_color = "#10B981" if score > 70 else "#F59E0B" if score > 40 else "#EF4444"
        
        st.markdown(f"""
        <div class="report-panel">
            <div class="report-title">Your Health Insights</div>
            
            <div class="score-container">
                <div class="score-label">
                    <span>Health Score</span>
                    <span style="color: {bar_color};">{score}/100</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width: {score}%; background: {bar_color};"></div>
                </div>
            </div>
            
            <div class="report-content">
                {formatted_report}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Reason Health Report", ln=True, align='C')
        pdf.set_font("Arial", size=11)
        clean_pdf_text = st.session_state.report_data.replace('**', '').replace('###', '').encode('ascii', 'ignore').decode('ascii')
        pdf.multi_cell(0, 8, clean_pdf_text)
        
        st.download_button("📥 Save My Health Report (PDF)", data=bytes(pdf.output()), file_name="My_Health_Report.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.markdown("""
        <div class="report-panel" style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 400px; text-align: center; border: 2px dashed #E2E8F0; background: #F8FAFC;">
            <div style="font-size: 4rem; margin-bottom: 10px; opacity: 0.4;">🫀</div>
            <div style="font-weight: 800; color: #475569; font-size: 1.2rem;">Your Health Insights</div>
            <p style="font-size: 0.9rem; color: #94A3B8; max-width: 80%;">Upload a lab report or chat with Reason to see your health score and simple advice here.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. CHAT INPUT
# ==========================================
if prompt := st.chat_input("How are you feeling today?"):
    if not api_key_input:
        st.error("API Key missing.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show Animated Heartbeat Loader
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
        <div class="heartbeat-loader">
            <svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            <span>Reason is thinking...</span>
        </div>
        """, unsafe_allow_html=True)
        
        sys_prompt = f"""
        You are Reason, a caring health guide.
        Patient: {st.session_state.profile['age']}y, {st.session_state.profile['gender']}, Weight: {st.session_state.profile['weight']}kg.
        
        The patient says: "{prompt}"
        Respond in very simple language. Be empathetic.
        
        FORMAT STRICTLY LIKE THIS:
        Health Score: [Number between 10 and 100]
        
        ### 📊 What This Might Mean
        [Explain in simple words]
        
        ### 💡 What You Should Do
        *   **Home Care:** [Advice]
        *   **Doctor Visit:** [Which doctor to see]
        """
        
        client = Groq(api_key=api_key_input)
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b", temperature=0.4
        ).choices[0].message.content
        
        loader_placeholder.empty()
        st.session_state.report_data = res
        st.session_state.messages.append({"role": "assistant", "content": "I have created a health insight for you. Please check the right panel."})
        st.rerun()
