import streamlit as st
import os
from groq import Groq

# --- PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="BioMind AI | Premium", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to BioMind. I am your advanced AI medical diagnostician. Please describe your symptoms in detail to begin the analysis."}
    ]

# --- FETCH API KEY ---
try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# --- DYNAMIC CSS (THE MASTERPIECE) ---
if st.session_state.theme == "dark":
    bg_color = "#0B0E14"
    text_color = "#F8FAFC"
    muted_color = "#94A3B8"
    sidebar_bg = "rgba(15, 20, 30, 0.95)"
    chat_user_bg = "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)"
    chat_ai_bg = "rgba(30, 41, 59, 0.6)"
    input_bg = "rgba(15, 20, 30, 0.8)"
    border_color = "rgba(255, 255, 255, 0.1)"
    glow = "rgba(99, 102, 241, 0.4)"
else:
    bg_color = "#F8FAFC"
    text_color = "#0F172A" 
    muted_color = "#64748B"
    sidebar_bg = "#FFFFFF"
    chat_user_bg = "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)"
    chat_ai_bg = "rgba(241, 245, 249, 0.8)"
    input_bg = "#FFFFFF"
    border_color = "rgba(0, 0, 0, 0.1)"
    glow = "rgba(99, 102, 241, 0.2)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

/* Global Fonts & Colors */
html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif !important; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; transition: background-color 0.5s ease; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 1200px; padding-top: 2rem; padding-bottom: 6rem; }}

/* --- SIDEBAR PREMIUM DESIGN --- */
[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {border_color};
    backdrop-filter: blur(20px);
}}
[data-testid="stSidebar"] * {{ color: {text_color} !important; }}

/* --- PREMIUM TOGGLE BUTTON --- */
div[data-testid="stToggle"] {{
    background: {chat_ai_bg};
    padding: 8px 16px;
    border-radius: 30px;
    border: 1px solid {border_color};
    width: fit-content;
    margin-left: auto;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}}

/* --- HERO TEXT --- */
.hero-container {{ text-align: center; margin-bottom: 50px; animation: fadeIn 1s ease-out; }}
.hero-title {{
    font-size: 4rem;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #00F0FF 0%, #7000FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}}
.hero-subtitle {{
    font-size: 1.1rem;
    color: {muted_color} !important;
    font-weight: 400;
    letter-spacing: 1px;
}}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

/* --- CHAT MESSAGES (GLASSMORPHISM) --- */
[data-testid="stChatMessage"] {{
    background: {chat_ai_bg};
    border: 1px solid {border_color};
    border-radius: 20px;
    padding: 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: slideUp 0.4s ease-out;
}}
[data-testid="stChatMessage"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 40px {glow};
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(15px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* User Message Specific Styling */
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {{
    background: {chat_user_bg} !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 8px 25px {glow};
}}
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * {{
    color: white !important;
}}

/* --- CHAT INPUT (FLOATING PILL) --- */
[data-testid="stChatInput"] {{ background: transparent !important; border: none !important; }}
[data-testid="stChatInput"] > div {{
    background: {input_bg} !important;
    border: 1px solid {border_color} !important;
    border-radius: 50px !important;
    padding: 8px 20px !important;
    backdrop-filter: blur(20px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease;
}}
[data-testid="stChatInput"]:focus-within > div {{
    border-color: #6366F1 !important;
    box-shadow: 0 0 25px {glow} !important;
}}
[data-testid="stChatInput"] textarea {{ color: {text_color} !important; caret-color: #6366F1 !important; }}
[data-testid="stChatInput"] textarea::placeholder {{ color: {muted_color} !important; }}

/* --- EMERGENCY BANNER (PULSING RED) --- */
.emergency-banner {{
    background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
    color: white !important;
    padding: 24px;
    border-radius: 16px;
    font-size: 1.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 24px;
    animation: pulse-red 2s infinite;
    box-shadow: 0 10px 30px rgba(239, 68, 68, 0.4);
    border: 1px solid #FCA5A5;
}}
@keyframes pulse-red {{
    0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
    70% {{ box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
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
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">BioMind AI</h1>
    <p class="hero-subtitle">ADVANCED MEDICAL DIAGNOSTICS & DISEASE DETECTIVE ENGINE</p>
</div>
""", unsafe_allow_html=True)

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    avatar = "🧬" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- SIDEBAR & KEY LOGIC ---
api_key_input = ""
with st.sidebar:
    st.markdown("<h2 style='font-size: 1.5rem; font-weight: 800; margin-bottom: 20px;'>⚙️ System Config</h2>", unsafe_allow_html=True)
    if SECRET_KEY:
        st.success("✅ API Key loaded securely from Secrets.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key not found. Please enter manually.")
        api_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

# --- INPUT LOGIC ---
if prompt := st.chat_input("Describe your symptoms here..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧬"):
        if not api_key_input:
            st.error("⚠️ API Key missing. Please check Streamlit Secrets or enter it in the sidebar.")
            st.stop()
            
        # 1. PYTHON-LEVEL EMERGENCY OVERRIDE
        is_emergency = check_emergency(prompt)
        
        if is_emergency:
            st.markdown("""
            <div class="emergency-banner">
                🚨 CALL EMERGENCY SERVICES (1122 / 911) IMMEDIATELY <br>
                <span style="font-size: 1rem; font-weight: 500; color: #FCA5A5;">Do not drive yourself. Unlock the door and wait for paramedics.</span>
            </div>
            """, unsafe_allow_html=True)

        with st.spinner("Analyzing medical database..."):
            try:
                client = Groq(api_key=api_key_input)
                
                system_prompt = """
                You are BioMind, an elite AI medical diagnostician.
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
