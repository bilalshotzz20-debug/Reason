import streamlit as st
import os
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(page_title="Reason | Clinical AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# State Init
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Reason. I am your advanced medical reasoning engine. Please describe your symptoms in detail to begin the analysis."}
    ]

try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# --- DYNAMIC CSS ---
if st.session_state.theme == "dark":
    bg_color = "#080C14"          # Midnight Navy
    text_color = "#F1F5F9"        # Off-White
    muted_color = "#94A3B8"       
    card_bg = "rgba(30, 41, 59, 0.4)" # Glass AI Bubble
    user_bg = "linear-gradient(135deg, #2563EB 0%, #06B6D4 100%)" # Modern Blue Gradient
    input_bg = "#1E293B"
    border_color = "rgba(255,255,255,0.1)"
else:
    bg_color = "#F4F7F9"          # Clinical Light Grey
    text_color = "#0F172A"        # Dark Slate
    muted_color = "#64748B"       
    card_bg = "#FFFFFF"           # Pure White AI Bubble
    user_bg = "linear-gradient(135deg, #2563EB 0%, #06B6D4 100%)" 
    input_bg = "#FFFFFF"
    border_color = "#E2E8F0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* --- GLOBAL --- */
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stApp {{
    background-color: {bg_color};
    color: {text_color};
    transition: background-color 0.4s ease;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 950px; padding-top: 2rem; padding-bottom: 6rem; }}

/* Force text visibility */
h1, h2, h3, h4, h5, h6, p, span, div, li {{
    color: {text_color} !important;
}}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] {{
    background-color: {card_bg} !important;
    border-right: 1px solid {border_color};
}}
[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

/* --- CUSTOM TOGGLE --- */
div[data-testid="stToggle"] {{
    background: {card_bg};
    padding: 6px 15px;
    border-radius: 30px;
    border: 1px solid {border_color};
    width: fit-content;
    margin-left: auto;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}}

/* --- HERO HEADER --- */
.hero {{
    text-align: center;
    margin-bottom: 40px;
    animation: fadeIn 0.8s ease-out;
}}
.hero h1 {{
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 5px;
}}
.hero p {{
    color: {muted_color} !important;
    font-size: 1rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(-10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* --- CHAT MESSAGES --- */
[data-testid="stChatMessage"] {{
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    animation: slideUp 0.4s ease-out;
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* User Message Specific */
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {{
    background: {user_bg} !important;
    border: none !important;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.2);
}}
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * {{
    color: #FFFFFF !important; /* Pure white text */
}}

/* --- CHAT INPUT --- */
[data-testid="stChatInput"] {{
    background-color: transparent !important;
}}
[data-testid="stChatInput"] > div {{
    background-color: {input_bg} !important;
    border: 1px solid {border_color} !important;
    border-radius: 30px !important; /* Pill shape */
    padding: 8px 16px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease;
}}
[data-testid="stChatInput"] > div:focus-within {{
    border-color: #2563EB !important;
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.2) !important;
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
    border-left: 6px solid #EF4444;
    color: #991B1B !important;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);
    animation: pulse-border 2s infinite;
}}
.emergency-banner span {{
    color: #7F1D1D !important;
    font-weight: 500;
    font-size: 0.95rem;
}}
@keyframes pulse-border {{
    0% {{ border-left-color: #EF4444; }}
    50% {{ border-left-color: #7F1D1D; }}
    100% {{ border-left-color: #EF4444; }}
}}

/* --- MOBILE RESPONSIVE --- */
@media (max-width: 768px) {{
    .block-container {{ padding: 1rem; }}
    .hero h1 {{ font-size: 2rem; }}
    [data-testid="stChatMessage"] {{ padding: 15px; }}
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
<div class="hero">
    <h1>🧠 Reason</h1>
    <p>Medical Reasoning Engine</p>
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
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700;'>⚙️ Configuration</h3>", unsafe_allow_html=True)
    if SECRET_KEY:
        st.success("✅ API Key connected.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key required.")
        api_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    st.divider()
    st.markdown("<p style='font-size: 0.8rem; color: gray;'>Disclaimer: Reason is an AI tool. Always consult a real doctor for medical emergencies.</p>", unsafe_allow_html=True)

# --- INPUT LOGIC ---
if prompt := st.chat_input("Describe your symptoms..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🩺"):
        if not api_key_input:
            st.error("⚠️ API Key missing. Please check the sidebar.")
            st.stop()
            
        # Python Fail-Safe
        is_emergency = check_emergency(prompt)
        
        if is_emergency:
            st.markdown("""
            <div class="emergency-banner">
                🚨 CALL EMERGENCY SERVICES (1122 / 911) IMMEDIATELY <br>
                <span>Do not drive yourself. Unlock the door and wait for paramedics.</span>
            </div>
            """, unsafe_allow_html=True)

        with st.spinner("Reasoning..."):
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
