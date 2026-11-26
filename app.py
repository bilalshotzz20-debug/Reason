import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import datetime

# --- PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Reason | Clinical AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Reason. I am your advanced medical reasoning engine. Please describe your symptoms in detail to begin the analysis."}
    ]

if "last_report" not in st.session_state:
    st.session_state.last_report = None

try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# --- DYNAMIC COLOR PALETTE & CSS ---
if st.session_state.theme == "dark":
    bg_color = "#0B1120"          
    text_color = "#F8FAFC"        
    muted_color = "#94A3B8"       
    chat_ai_bg = "#1E293B"        
    chat_user_bg = "linear-gradient(135deg, #06B6D4 0%, #4F46E5 100%)" 
    input_bg = "#1E293B"
    border_color = "#334155"
    glow = "rgba(6, 182, 212, 0.15)"
else:
    bg_color = "#F4F7FB"          
    text_color = "#0F172A"        
    muted_color = "#64748B"       
    chat_ai_bg = "#FFFFFF"        
    chat_user_bg = "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)" 
    input_bg = "#FFFFFF"
    border_color = "#E2E8F0"
    glow = "rgba(14, 165, 233, 0.15)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif !important; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; transition: background-color 0.4s ease; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 950px; padding-top: 2rem; padding-bottom: 6rem; }}
h1, h2, h3, h4, h5, h6, p, span, div, li {{ color: {text_color} !important; }}

[data-testid="stSidebar"] {{ background-color: {bg_color} !important; border-right: 1px solid {border_color}; }}
[data-testid="stSidebar"] * {{ color: {text_color} !important; }}

div[data-testid="stToggle"] {{ background: {chat_ai_bg}; padding: 6px 16px; border-radius: 30px; border: 1px solid {border_color}; width: fit-content; margin-left: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }}

.hero {{ text-align: center; margin-bottom: 40px; animation: fadeIn 0.8s ease-out; }}
.hero h1 {{ font-size: 3rem; font-weight: 700; letter-spacing: -1.5px; margin-bottom: 5px; }}
.hero p {{ color: {muted_color} !important; font-size: 0.95rem; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

[data-testid="stChatMessage"] {{ background-color: {chat_ai_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); animation: slideUp 0.4s ease-out; }}
@keyframes slideUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {{ background: {chat_user_bg} !important; border: none !important; box-shadow: 0 8px 25px {glow}; }}
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * {{ color: #FFFFFF !important; }}

[data-testid="stChatInput"] {{ background-color: transparent !important; }}
[data-testid="stChatInput"] > div {{ background-color: {input_bg} !important; border: 1px solid {border_color} !important; border-radius: 40px !important; padding: 10px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important; }}
[data-testid="stChatInput"] > div:focus-within {{ border-color: #2563EB !important; box-shadow: 0 0 15px {glow} !important; }}
[data-testid="stChatInput"] textarea {{ color: {text_color} !important; }}
[data-testid="stChatInput"] textarea::placeholder {{ color: {muted_color} !important; }}

.emergency-banner {{ background-color: #FEF2F2; border-left: 5px solid #EF4444; color: #991B1B !important; padding: 18px 20px; border-radius: 8px; margin-bottom: 20px; font-weight: 700; font-size: 1.05rem; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1); }}
.emergency-banner span {{ color: #7F1D1D !important; font-weight: 500; font-size: 0.9rem; }}

/* Download Button Styling */
.stDownloadButton > button {{
    background-color: transparent;
    border: 1px solid {border_color};
    color: {text_color};
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s;
}}
.stDownloadButton > button:hover {{
    border-color: #2563EB;
    background-color: {chat_ai_bg};
}}

@media (max-width: 768px) {{ .block-container {{ padding: 1rem; }} .hero h1 {{ font-size: 2.2rem; }} [data-testid="stChatMessage"] {{ padding: 16px; }} }}
</style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR FUNCTION ---
def generate_pdf_report(report_text, symptoms):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(37, 99, 235) # Medical Blue
    pdf.cell(0, 10, "Reason Medical Diagnostics Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, f"Generated on: {date_str}", ln=True, align='C')
    pdf.ln(10)
    
    # Patient Symptoms
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Reported Symptoms:", ln=True)
    pdf.set_font("Arial", size=11)
    # Remove non-ascii characters for fpdf
    clean_symptoms = symptoms.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 8, clean_symptoms)
    pdf.ln(5)
    
    # AI Report
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AI Diagnostic Assessment:", ln=True)
    pdf.set_font("Arial", size=11)
    
    # Clean markdown for PDF
    clean_text = report_text.replace('**', '').replace('###', '').replace('*', '-')
    clean_text = clean_text.encode('ascii', 'ignore').decode('ascii') # Strip emojis for PDF compatibility
    
    pdf.multi_cell(0, 8, clean_text)
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 6, "Disclaimer: This report is generated by an AI and is not a substitute for professional medical diagnosis. Please consult a doctor immediately.")
    
    return bytes(pdf.output())

# --- EMERGENCY KEYWORD CHECKER ---
def check_emergency(symptoms_text):
    symptoms_text = symptoms_text.lower()
    emergency_keywords = ["chest pain", "heart attack", "radiating to left arm", "crushing chest", "stroke", "slurred speech", "facial drooping", "arm weakness", "severe bleeding", "cannot breathe", "shortness of breath", "suicidal", "want to die", "overdose"]
    for keyword in emergency_keywords:
        if keyword in symptoms_text:
            return True
    return False

# --- TOP BAR ---
col1, col2 = st.columns([4, 1])
with col2:
    is_dark = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
    if is_dark and st.session_state.theme == "light":
        st.session_state.theme = "dark"
        st.rerun()
    elif not is_dark and st.session_state.theme == "dark":
        st.session_state.theme = "light"
        st.rerun()

st.markdown("""
<div class="hero">
    <h1>🧠 Reason</h1>
    <p>Advanced Medical Reasoning Engine</p>
</div>
""", unsafe_allow_html=True)

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    avatar = "🩺" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- SIDEBAR ---
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
                
                # NEW STRUCTURED PROMPT FOR REPORT GENERATION
                system_prompt = """
                You are Reason, an elite AI medical diagnostician.
                Analyze the patient's symptoms and provide a structured, professional medical report.
                
                YOU MUST FORMAT YOUR RESPONSE EXACTLY LIKE THIS USING MARKDOWN:

                ### 📋 Patient Summary
                [1-2 sentences summarizing the patient's reported symptoms and presentation.]

                ### 🦠 Top Possible Conditions (Diagnosis)
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
                
                # SAVE REPORT TO SESSION STATE FOR PDF GENERATION
                st.session_state.last_report = response
                st.session_state.last_symptoms = prompt
                
            except Exception as e:
                st.error(f"System Error: {str(e)}")

# --- PDF DOWNLOAD BUTTON ---
if st.session_state.last_report:
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(st.session_state.last_report, st.session_state.last_symptoms)
    
    st.download_button(
        label="📥 Download Official Medical Report (PDF)",
        data=pdf_bytes,
        file_name=f"Reason_Medical_Report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
