import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import datetime
import pypdf

# --- PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Reason | Clinical Diagnostics", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Reason. I am your advanced medical reasoning engine. Please describe your symptoms or upload a medical report to begin."}
    ]

if "last_report" not in st.session_state:
    st.session_state.last_report = None

try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# --- FIXED MEDICAL COLOR PALETTE ---
bg_color = "#F4F7FB"          # Clinical Light Icy Blue
text_color = "#0F172A"        # Deep Slate (Almost black, better than pure black)
muted_color = "#64748B"       # Slate grey
chat_ai_bg = "#FFFFFF"        # Pure white
chat_user_bg = "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)" # Medical Blue Gradient
input_bg = "#FFFFFF"
border_color = "#E2E8F0"
glow = "rgba(14, 165, 233, 0.15)"
uploader_bg = "#FFFFFF"
uploader_border = "#CBD5E1"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* --- GLOBAL --- */
html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif !important; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 950px; padding-top: 2rem; padding-bottom: 6rem; }}

/* Force text visibility */
h1, h2, h3, h4, h5, h6, p, span, div, li {{ color: {text_color} !important; }}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] {{ background-color: {bg_color} !important; border-right: 1px solid {border_color}; }}
[data-testid="stSidebar"] * {{ color: {text_color} !important; }}

/* --- HERO HEADER --- */
.hero {{ text-align: center; margin-bottom: 30px; animation: fadeIn 0.8s ease-out; }}
.hero h1 {{ font-size: 3.5rem; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 5px; color: #1E3A8A !important; }}
.hero p {{ color: {muted_color} !important; font-size: 0.95rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

/* --- CHAT MESSAGES --- */
[data-testid="stChatMessage"] {{ background-color: {chat_ai_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); animation: slideUp 0.4s ease-out; }}
@keyframes slideUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {{ background: {chat_user_bg} !important; border: none !important; box-shadow: 0 8px 25px {glow}; }}
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * {{ color: #FFFFFF !important; }}

/* --- CHAT INPUT --- */
[data-testid="stChatInput"] {{ background-color: transparent !important; }}
[data-testid="stChatInput"] > div {{ background-color: {input_bg} !important; border: 1px solid {border_color} !important; border-radius: 40px !important; padding: 10px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important; }}
[data-testid="stChatInput"] > div:focus-within {{ border-color: #2563EB !important; box-shadow: 0 0 15px {glow} !important; }}
[data-testid="stChatInput"] textarea {{ color: {text_color} !important; }}

/* --- EMERGENCY BANNER --- */
.emergency-banner {{ background-color: #FEF2F2; border-left: 6px solid #EF4444; color: #991B1B !important; padding: 20px; border-radius: 8px; margin-bottom: 20px; font-weight: 800; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1); }}
.emergency-banner span {{ color: #7F1D1D !important; font-weight: 500; font-size: 0.95rem; }}

/* --- TABS --- */
.stTabs [data-baseweb="tab-list"] {{ gap: 24px; border-bottom: 2px solid {border_color}; }}
.stTabs [data-baseweb="tab"] {{ height: 50px; white-space: pre-wrap; background-color: transparent; gap: 1px; padding-top: 10px; padding-bottom: 10px; }}
.stTabs [aria-selected="true"] {{ background-color: {chat_ai_bg}; border-bottom: 3px solid #2563EB; }}
.stTabs [data-baseweb="tab"] p {{ color: {muted_color} !important; font-weight: 700; }}
.stTabs [aria-selected="true"] p {{ color: #1E3A8A !important; }}

/* --- FILE UPLOADER --- */
[data-testid="stFileUploader"] {{ background-color: transparent !important; }}
[data-testid="stFileUploadDropzone"] {{ background-color: {uploader_bg} !important; border: 2px dashed {uploader_border} !important; border-radius: 12px !important; padding: 20px !important; }}
[data-testid="stFileUploadDropzone"]:hover {{ border-color: #2563EB !important; }}
[data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploadDropzone"] div {{ color: {text_color} !important; }}
[data-testid="stFileUploadDropzone"] button {{ background-color: {bg_color} !important; color: #2563EB !important; border: 1px solid #2563EB !important; border-radius: 8px !important; font-weight: 600; }}

/* --- BUTTONS --- */
.stButton > button {{ background-color: #2563EB !important; color: white !important; border-radius: 8px !important; font-weight: 600; padding: 10px 24px; }}
.stButton > button:hover {{ background-color: #1D4ED8 !important; border-color: #1D4ED8 !important; color: white !important; }}

/* --- DOWNLOAD BUTTON --- */
.stDownloadButton > button {{ background-color: #10B981 !important; color: white !important; border-radius: 8px !important; font-weight: 600; padding: 10px 24px; border: none !important; }}
.stDownloadButton > button:hover {{ background-color: #059669 !important; }}

@media (max-width: 768px) {{ .block-container {{ padding: 1rem; }} .hero h1 {{ font-size: 2.2rem; }} }}
</style>
""", unsafe_allow_html=True)

# --- PDF EXTRACTION FUNCTION ---
def extract_text_from_pdf(pdf_file):
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# --- PDF GENERATOR FUNCTION ---
def generate_pdf_report(report_text, symptoms):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "Reason Clinical Diagnostics Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, f"Generated on: {date_str}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Source Data (Symptoms/Report):", ln=True)
    pdf.set_font("Arial", size=11)
    clean_symptoms = symptoms.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 8, clean_symptoms[:1000] + "...") 
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Diagnostic Assessment:", ln=True)
    pdf.set_font("Arial", size=11)
    clean_text = report_text.replace('**', '').replace('###', '').replace('*', '-')
    clean_text = clean_text.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 8, clean_text)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 6, "Disclaimer: This report is generated by Reason and is not a substitute for professional medical diagnosis. Please consult a doctor.")
    return bytes(pdf.output())

# --- EMERGENCY KEYWORD CHECKER ---
def check_emergency(symptoms_text):
    symptoms_text = symptoms_text.lower()
    emergency_keywords = ["chest pain", "heart attack", "radiating to left arm", "crushing chest", "stroke", "slurred speech", "facial drooping", "arm weakness", "severe bleeding", "cannot breathe", "shortness of breath", "suicidal", "want to die", "overdose"]
    for keyword in emergency_keywords:
        if keyword in symptoms_text:
            return True
    return False

# --- HEADER ---
st.markdown("""
<div class="hero">
    <h1>🧠 Reason</h1>
    <p>Advanced Medical Reasoning Engine</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
api_key_input = ""
with st.sidebar:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 800; color: #1E3A8A;'>⚙️ System Settings</h3>", unsafe_allow_html=True)
    if SECRET_KEY:
        st.success("✅ API Key connected securely.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key required.")
        api_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    st.divider()
    st.markdown("<p style='font-size: 0.85rem; color: #64748B;'><b>Disclaimer:</b> Reason is a clinical diagnostics system. It does not replace a real doctor. Always consult a medical professional for emergencies.</p>", unsafe_allow_html=True)

# --- TABS CREATION ---
tab1, tab2 = st.tabs(["🩺 Symptom Chat", "📄 Upload Medical Report"])

# ==========================================
# TAB 1: SYMPTOM CHAT
# ==========================================
with tab1:
    for message in st.session_state.messages:
        avatar = "🩺" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Describe your symptoms..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🩺"):
            if not api_key_input:
                st.error("⚠️ API Key missing. Please check the sidebar.")
                st.stop()
                
            if check_emergency(prompt):
                st.markdown("""
                <div class="emergency-banner">
                    🚨 CALL EMERGENCY SERVICES (1122 / 911) IMMEDIATELY <br>
                    <span>Do not drive yourself. Unlock the door and wait for paramedics.</span>
                </div>
                """, unsafe_allow_html=True)

            with st.spinner("Reasoning through medical data..."):
                try:
                    client = Groq(api_key=api_key_input)
                    system_prompt = """
                    You are Reason, an elite medical diagnostician.
                    Analyze the patient's symptoms and provide a structured, professional medical report.
                    IMPORTANT: Never refer to yourself as an AI. You are Reason.
                    
                    FORMAT:
                    ### 📋 Patient Summary
                    [1 sentence]
                    ### 🦠 Top Possible Conditions
                    **1. [Condition]**
                    *Why it fits:* [1 sentence]
                    **2. [Condition]**
                    *Why it fits:* [1 sentence]
                    **3. [Condition]**
                    *Why it fits:* [1 sentence]
                    ### 🚨 Urgency Level
                    **[Low / Medium / High / CRITICAL]**
                    [1 sentence]
                    ### 🧪 Recommended Next Steps
                    *   **[Test]:** [Why needed]
                    *   **[Action]:** [Consult specialist]
                    """
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                        model="openai/gpt-oss-120b",
                        temperature=0.2, 
                    )
                    response = chat_completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.last_report = response
                    st.session_state.last_symptoms = prompt
                except Exception as e:
                    st.error(f"System Error: {str(e)}")

# ==========================================
# TAB 2: UPLOAD MEDICAL REPORT
# ==========================================
with tab2:
    st.markdown("### 📄 Upload Lab Report or Prescription (PDF)")
    st.markdown("<p style='color: #64748B;'>Reason will extract the text, analyze the values, and provide a diagnosis and recommendations.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload PDF Report", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        if st.button("Analyze Report", use_container_width=True):
            if not api_key_input:
                st.error("⚠️ API Key missing. Please check the sidebar.")
                st.stop()
                
            with st.spinner("Extracting text from PDF..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
                
            if "Error" in extracted_text:
                st.error(extracted_text)
            elif len(extracted_text.strip()) < 20:
                st.warning("Could not extract readable text from this PDF. It might be a scanned image.")
            else:
                st.success("Text extracted successfully!")
                with st.expander("View Extracted Text"):
                    st.text(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)
                
                with st.spinner("Reasoning through medical report..."):
                    try:
                        client = Groq(api_key=api_key_input)
                        
                        system_prompt_report = """
                        You are Reason, an elite medical diagnostician. 
                        I am providing you with the text extracted from a patient's medical report/lab results.
                        Analyze the data (lab values, clinical notes) and provide a structured report.
                        IMPORTANT: Never refer to yourself as an AI. You are Reason.
                        
                        FORMAT:
                        ### 📋 Key Findings (Abnormalities)
                        [List any abnormal values or key findings from the report]
                        ### 🦠 Top Possible Conditions (Diagnosis)
                        **1. [Condition Name]**
                        *Why it fits:* [Explain based on the report data]
                        **2. [Condition Name]**
                        *Why it fits:* [Explain]
                        ### 🚨 Urgency Level
                        **[Low / Medium / High / CRITICAL]**
                        [Explain why]
                        ### 🧪 Recommendations & Next Steps
                        *   **[Action]:** [E.g., Consult a Hematologist, start medication]
                        *   **[Diet/Lifestyle]:** [Advice based on findings]
                        """
                        
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": system_prompt_report},
                                {"role": "user", "content": f"Here is my medical report text:\n\n{extracted_text}"}
                            ],
                            model="openai/gpt-oss-120b",
                            temperature=0.1, 
                        )
                        
                        response = chat_completion.choices[0].message.content
                        st.markdown("---")
                        st.markdown(response)
                        
                        st.session_state.last_report = response
                        st.session_state.last_symptoms = "Uploaded Medical Report Analysis"
                        
                    except Exception as e:
                        st.error(f"System Error: {str(e)}")

# --- PDF DOWNLOAD BUTTON ---
if st.session_state.last_report:
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(st.session_state.last_report, st.session_state.last_symptoms)
    
    st.download_button(
        label="📥 Download Official Medical Report (PDF)",
        data=pdf_bytes,
        file_name=f"Reason_Report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
