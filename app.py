import streamlit as st
import os
from groq import Groq

# --- PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Reason | Medical Diagnostics", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state.theme = "light" # Clinical Light Mode by Default

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Reason. I am your advanced medical reasoning engine. Please describe your symptoms in detail to begin the analysis."}
    ]

# --- FETCH API KEY ---
try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# --- DYNAMIC CSS (CLEAN MEDICAL UI) ---
if st.session_state.theme == "dark":
    bg_color = "#0F172A"          
    text_color = "#F8FAFC"        
    muted_color = "#94A3B8"       
    chat_ai_bg = "#1E293B"        
    chat_user_bg = "#0EA5E9"      
    input_bg = "#1E293B"
    border_color = "#334155"
else:
    bg_color = "#F8FAFC"          
    text_color = "#1E293B"        
    muted_color = "#64748B"       
    chat_ai_bg = "#FFFFFF"        
    chat_user_bg = "#0EA5E9"      
    input_bg = "#FFFFFF"
    border_color = "#E2E8F0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* --- GLOBAL STYLES --- */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}
.stApp {{
    background-color: {bg_color};
    color: {text_color};
    transition: background-color 0.4s ease, color 0.4s ease;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 1000px; padding-top: 2rem; padding-bottom: 5rem; }}

/* Force text colors */
p, span, li, h1, h2, h3, h4, h5, h6, div {{
    color: {text_color} !important;
}}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] {{
    background-color: {bg_color} !important;
    border-right: 1px solid {border_color};
}}
[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

/* --- CHAT MESSAGES --- */
[data-testid="stChatMessage"] {{
    background-color: {chat_ai_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}}

/* User Chat Bubble */
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {{
    background-color: {chat_user_bg} !important;
    border: none !important;
}}
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * {{
    color: #FFFFFF !important; /* White text on Medical Blue */
}}

/* --- CHAT INPUT BOX --- */
[data-testid="stChatInput"] {{
    background-color: transparent !important;
}}
[data-testid="stChatInput"] > div {{
    background-color: {input_bg} !important;
    border: 1px solid {border_color} !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: {text_color} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {muted_color} !important;
}}

/* --- EMERGENCY BANNER --- */
.emergency-banner {{
    background-color: #FEF2F2;
    border-left: 4px solid #EF4444;
    color: #991B1B !important;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-weight: 600;
}}
.emergency-banner span {{
    color: #7F1D1D !important;
    font-weight: 400;
    font-size: 0.9rem;
}}

/* --- RESPONSIVE FOR MOBILE --- */
@media (max-width: 768px) {{
    .block-container {{ padding-top: 1rem; padding-bottom: 4rem; }}
    [data-testid="stChatMessage"] {{ padding: 15px; }}
    .hero-title {{ font-size: 2rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

# --- EMERGENCY KEYWORD CHECKER ---
def check_emergency(symptoms_text):
    symptoms_text = symptoms_text.lower()
    emergency_keywords = ["chest pain", "heart attack", "radiating to left arm", "crushing chest", "stroke", "slurred speech", "facial drooping", "arm weakness", "severe bleeding", "cannot breathe", "shortness of breath", "suicidal", "want to die", "overdose"]
    for keyword in emergency_keywords:
        if keyword in symptoms_text:
            return True
    return False

# --- TOP BAR (Theme Toggle) ---
col1, col2 = st.columns([4, 1])
with col2:
    is_dark = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
    if is_dark and st.session_state.theme == "light":
        st.session_state.theme = "dark"
        st.rerun()
    elif not is_dark and st.session_state.theme == "dark":
        st.session_state.theme = "light"
        st.rerun()

# --- HERO SECTION ---
st.markdown(f"""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="font-size: 3rem; font-weight: 700; color: {text_color}; margin-bottom: 5px;">🧠 Reason</h1>
    <p style="color: {muted_color}; font-size: 1rem; letter-spacing: 1px;">ADVANCED MEDICAL DIAGNOSTICS & REASONING ENGINE</p>
</div>
""", unsafe_allow_html=True)

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    avatar = "🩺" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- SIDEBAR & KEY LOGIC ---
api_key_input = ""
with st.sidebar:
    st.markdown("<h2 style='font-size: 1.2rem; font-weight: 600;'>⚙️ System Config</h2>", unsafe_allow_html=True)
    if SECRET_KEY:
        st.success("✅ API Key loaded from Secrets.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key missing.")
        api_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    st.divider()
    st.markdown("<p style='font-size: 0.8rem; color: gray;'>Disclaimer: Reason is an AI assistant, not a replacement for professional medical advice.</p>", unsafe_allow_html=True)

# --- INPUT LOGIC ---
if prompt := st.chat_input("Describe your symptoms..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🩺"):
        if not api_key_input:
            st.error("⚠️ API Key missing.")
            st.stop()
            
        # Python Fail-Safe
        is_emergency = check_emergency(prompt)
        
        if is_emergency:
            st.markdown(f"""
            <div class="emergency-banner">
                🚨 CALL EMERGENCY SERVICES (1122 / 911) IMMEDIATELY <br>
                <span>Do not drive yourself. Unlock the door and wait for paramedics.</span>
            </div>
            """, unsafe_allow_html=True)

        with st.spinner("Reasoning through medical database..."):
            try:
                client = Groq(api_key=api_key_input)
                
                system_prompt = """
                You are Reason, an elite AI medical diagnostician.
                Analyze the patient's symptoms and provide a structured, professional medical report.
                
                YOU MUST FORMAT YOUR RESPONSE EXACTLY LIKE THIS USING MARKDOWN:

                ### 🦠 Top Possible Conditions
                **1. [Condition Name]**
                *Why it fits:* [1 sentence explanation]
                **2. [Condition Name]**
                *Why it fits:* [1 sentence explanation]
                **3. [Condition Name]**
                *Why it fits:* [1 sentence explanation]

                ### 🚨 Urgency Level
                **[Low / Medium / High / CRITICAL]**
                [1 sentence explaining the urgency]

                ### 🧪 Recommended Next Steps
                *   **[Test Name]:** [Why this test is needed]
                *   **[Action]:** [E.g., Consult a specialist]

                ---
                *⚕️ Disclaimer: I am an AI assistant. This is not a substitute for professional medical diagnosis. Please consult a doctor immediately.*
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="openai/gpt-oss-120b",
                    temperature=0.2, 
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"System Error: {str(e)}")
