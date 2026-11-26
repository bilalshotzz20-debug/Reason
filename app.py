import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import datetime
import pypdf

# --- PAGE CONFIG ---
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

# --- FORCED CLINICAL LIGHT CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* GLOBAL SETTINGS */
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 950px; padding-top: 2rem; padding-bottom: 6rem; }

/* FORCE ALL TEXT TO BE DARK AND VISIBLE */
h1, h2, h3, h4, h5, h6, p, span, div, li, label, small { 
    color: #0F172A !important; 
}

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
[data-testid="stSidebar"] * { color: #0F172A !important; }
[data-testid="stSidebar"] input { color: #0F172A !important; background-color: #F8FAFC !important; border: 1px solid #CBD5E1 !important; }

/* HERO HEADER */
.hero { text-align: center; margin-bottom: 30px; }
.hero h1 { font-size: 3.5rem; font-weight: 800; color: #1E3A8A !important; margin-bottom: 5px; }
.hero p { color: #475569 !important; font-size: 0.95rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }

/* CHAT MESSAGES */
[data-testid="stChatMessage"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important; }
[data-testid="stChatMessage"] * { color: #0F172A !important; }
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) { background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important; border: none !important; }
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * { color: #FFFFFF !important; }

/* CHAT INPUT BOX */
[data-testid="stChatInput"] { background-color: transparent !important; }
[data-testid="stChatInput"] > div { background-color: #FFFFFF !important; border: 2px solid #CBD5E1 !important; border-radius: 40px !important; padding: 10px 20px !important; }
[data-testid="stChatInput"] > div:focus-within { border-color: #2563EB !important; box-shadow: 0 0 15px rgba(37, 99, 235, 0.2) !important; }
[data-testid="stChatInput"] textarea { color: #0F172A !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #64748B !important; }

/* EMERGENCY BANNER */
.emergency-banner { background-color: #FEF2F2 !important; border-left: 6px solid #EF4444 !important; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.emergency-banner * { color: #991B1B !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 2px solid #E2E8F0; }
.stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; }
.stTabs [data-baseweb="tab"] p { color: #475569 !important; font-weight: 700; font-size: 1.05rem; }
.stTabs [aria-selected="true"] { border-bottom: 3px solid #2563EB; }
.stTabs [aria-selected="true"] p { color: #1E3A8A !important; }

/* FILE UPLOADER (FORCED WHITE) */
[data-testid="stFileUploader"] { background-color: transparent !important; }
[data-testid="stFileUploadDropzone"] { 
    background-color: #FFFFFF !important; 
    border: 2px dashed #94A3B8 !important; 
    border-radius: 12px !important; 
    padding: 20px !important; 
}
[data-testid="stFileUploadDropzone"] * { color: #0F172A !important; }
[data-testid="stFileUploadDropzone"] button { 
    background-color: #2563EB !important; 
    border: none !important; 
    border-radius: 8px !important; 
}
[data-testid="stFileUploadDropzone"] button * { color: #FFFFFF !important; }

/* STANDARD BUTTONS */
.stButton > button { background-color: #2563EB !important; border: none !important; border-radius: 8px !important; width: 100%; padding: 12px; }
.stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
.stButton > button:hover { background-color: #1D4ED8 !important; }

/* DOWNLOAD BUTTON */
.stDownloadButton > button { background-color: #10B981 !important; border: none !important; border-radius: 8px !important; width: 100%; padding: 12px; }
.stDownloadButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
.stDownloadButton > button:hover { background-color: #059669 !important; }

/* EXPANDER */
[data-testid="stExpander"] { border: 1px solid #E2E8F0 !important; border-radius: 8px; background-color: #FFFFFF !important; }
[data-testid="stExpander"] * { color: #0F172A !important; }

</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def extract_text_from_pdf(pdf_file):
    try:
        reader = pypdf.PdfReader(pdf_file)
        return "".join([page.extract_text() + "\n" for page in reader.pages])
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def generate_pdf_report(report_text, symptoms):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "Reason Clinical Diagnostics Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Source Data (Symptoms/Report):", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, symptoms.encode('ascii', 'ignore').decode('ascii')[:1000] + "...") 
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Diagnostic Assessment:", ln=True)
    pdf.set_font("Arial", size=11)
    clean_text = report_text.replace('**', '').replace('###', '').replace('*', '-').encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 8, clean_text)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 6, "Disclaimer: This report is generated by Reason and is not a substitute for professional medical diagnosis. Please consult a doctor.")
    return bytes(pdf.output())

def check_emergency(symptoms_text):
    text = symptoms_text.lower()
    keywords = ["chest pain", "heart attack", "radiating to left arm", "crushing chest", "stroke", "slurred speech", "facial drooping", "arm weakness", "severe bleeding", "cannot breathe", "shortness of breath", "suicidal", "want to die", "overdose"]
    return any(k in text for k in keywords)

# --- MAIN UI ---
st.markdown('<div class="hero"><h1>🧠 Reason</h1><p>Advanced Medical Reasoning Engine</p></div>', unsafe_allow_html=True)

api_key_input = ""
with st.sidebar:
    st.markdown("### ⚙️ System Settings")
    if SECRET_KEY:
        st.success("✅ API Key connected securely.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key required.")
        api_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.divider()
    st.markdown("<p style='font-size: 0.85rem;'><b>Disclaimer:</b> Reason does not replace a real doctor. Consult a professional for emergencies.</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🩺 Symptom Chat", "📄 Upload Medical Report"])

with tab1:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🩺" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    if prompt := st.chat_input("Describe your symptoms..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🩺"):
            if not api_key_input:
                st.error("⚠️ API Key missing.")
                st.stop()
            if check_emergency(prompt):
                st.markdown('<div class="emergency-banner">🚨 CALL EMERGENCY SERVICES (1122 / 911) IMMEDIATELY <br><span>Do not drive yourself. Unlock the door and wait for paramedics.</span></div>', unsafe_allow_html=True)

            with st.spinner("Reasoning..."):
                try:
                    client = Groq(api_key=api_key_input)
                    sys_prompt = "You are Reason, an elite medical diagnostician. Never refer to yourself as AI. FORMAT: ### 📋 Patient Summary [1 sentence] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [1 sentence] **2. [Condition]** *Why it fits:* [1 sentence] **3. [Condition]** *Why it fits:* [1 sentence] ### 🚨 Urgency Level **[Low / Medium / High / CRITICAL]** [1 sentence] ### 🧪 Recommended Next Steps * **[Test]:** [Why needed] * **[Action]:** [Consult specialist]"
                    res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}], model="openai/gpt-oss-120b", temperature=0.2).choices[0].message.content
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.session_state.last_report = res
                    st.session_state.last_symptoms = prompt
                except Exception as e:
                    st.error(f"System Error: {str(e)}")

with tab2:
    st.markdown("### 📄 Upload Lab Report (PDF)")
    st.markdown("<p>Reason will extract values and provide a diagnosis.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file and st.button("Analyze Report", use_container_width=True):
        if not api_key_input:
            st.error("⚠️ API Key missing.")
            st.stop()
        with st.spinner("Extracting..."):
            extracted = extract_text_from_pdf(uploaded_file)
            
        if "Error" in extracted or len(extracted.strip()) < 20:
            st.error("Could not read PDF text.")
        else:
            st.success("Text extracted!")
            with st.expander("View Extracted Text"):
                st.text(extracted[:1000] + "...")
            
            with st.spinner("Reasoning..."):
                try:
                    client = Groq(api_key=api_key_input)
                    sys_prompt = "You are Reason. Analyze this medical report. Never refer to yourself as AI. FORMAT: ### 📋 Key Findings [list] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [explain] ### 🚨 Urgency Level **[Level]** [explain] ### 🧪 Recommendations * **[Action]:** [advice]"
                    res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": extracted}], model="openai/gpt-oss-120b", temperature=0.1).choices[0].message.content
                    st.markdown("---")
                    st.markdown(res)
                    st.session_state.last_report = res
                    st.session_state.last_symptoms = "Uploaded Report"
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if st.session_state.last_report:
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(st.session_state.last_report, st.session_state.last_symptoms)
    st.download_button("📥 Download Official Report (PDF)", data=pdf_bytes, file_name="Reason_Report.pdf", mime="application/pdf", use_container_width=True)
