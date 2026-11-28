import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import datetime
import pypdf

# --- PAGE CONFIG ---
st.set_page_config(page_title="Reason | Clinical Diagnostics", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
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

# --- VIBRANT COLORFUL CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* GLOBAL BACKGROUND & FONTS */
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { 
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    background-image: radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.1) 0px, transparent 50%), 
                      radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.1) 0px, transparent 50%);
    color: #0F172A !important; 
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 950px; padding-top: 2rem; padding-bottom: 6rem; }

/* TEXT VISIBILITY */
h1, h2, h3, h4, h5, h6, p, span, div, li, label { color: #0F172A !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: rgba(255,255,255,0.9) !important; backdrop-filter: blur(10px); border-right: 1px solid #E2E8F0 !important; }
[data-testid="stSidebar"] * { color: #0F172A !important; }

/* HERO TITLE (GRADIENT TEXT) */
.hero { text-align: center; margin-bottom: 30px; }
.hero h1 { 
    font-size: 3.5rem; font-weight: 800; margin-bottom: 5px; 
    background: -webkit-linear-gradient(45deg, #8B5CF6, #EC4899, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p { color: #64748B !important; font-size: 0.95rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }

/* CHAT BUBBLES */
[data-testid="stChatMessage"] { 
    background-color: #FFFFFF !important; 
    border: 1px solid #E2E8F0 !important; 
    border-radius: 20px; 
    padding: 20px; 
    margin-bottom: 20px; 
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important; 
}
[data-testid="stChatMessage"] * { color: #0F172A !important; }

/* User Chat Bubble (Vibrant Gradient) */
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) { 
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important; 
    border: none !important; 
    box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4) !important;
}
[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) * { color: #FFFFFF !important; }

/* CHAT INPUT */
[data-testid="stChatInput"] { background-color: transparent !important; }
[data-testid="stChatInput"] > div { 
    background-color: #FFFFFF !important; 
    border: 2px solid #C7D2FE !important; 
    border-radius: 40px !important; 
    padding: 10px 20px !important; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease;
}
[data-testid="stChatInput"] > div:focus-within { 
    border-color: #8B5CF6 !important; 
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.3) !important; 
}
[data-testid="stChatInput"] textarea { color: #0F172A !important; }

/* EMERGENCY BANNER */
.emergency-banner { 
    background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%) !important; 
    border-left: 6px solid #EF4444 !important; 
    padding: 20px; 
    border-radius: 12px; 
    margin-bottom: 20px; 
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    animation: pulse-red 2s infinite;
}
.emergency-banner * { color: #991B1B !important; }
@keyframes pulse-red {
    0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
    100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* TABS (Colorful Active State) */
.stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 2px solid #E2E8F0; }
.stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; }
.stTabs [data-baseweb="tab"] p { color: #64748B !important; font-weight: 700; font-size: 1.05rem; }
.stTabs [aria-selected="true"] { 
    background: linear-gradient(90deg, #8B5CF6, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    border-bottom: 3px solid #8B5CF6; 
}
.stTabs [aria-selected="true"] p { 
    background: -webkit-linear-gradient(45deg, #8B5CF6, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] { background-color: transparent !important; }
[data-testid="stFileUploadDropzone"] { 
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%) !important; 
    border: 2px dashed #A78BFA !important; 
    border-radius: 16px !important; 
    padding: 30px !important; 
    transition: all 0.3s;
}
[data-testid="stFileUploadDropzone"]:hover { border-color: #8B5CF6 !important; background: #F5F3FF !important; }
[data-testid="stFileUploadDropzone"] * { color: #0F172A !important; }
[data-testid="stFileUploadDropzone"] button { 
    background: linear-gradient(135deg, #8B5CF6, #6366F1) !important; 
    border: none !important; 
    border-radius: 8px !important; 
    padding: 8px 16px;
}
[data-testid="stFileUploadDropzone"] button * { color: #FFFFFF !important; }

/* BUTTONS */
.stButton > button { 
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important; 
    border: none !important; 
    border-radius: 12px !important; 
    width: 100%; 
    padding: 14px; 
    transition: 0.3s;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5); }
.stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; font-size: 1rem;}

.stDownloadButton > button { 
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; 
    border: none !important; 
    border-radius: 12px !important; 
    width: 100%; 
    padding: 14px;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}
.stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5); }
.stDownloadButton > button * { color: #FFFFFF !important; font-weight: 700 !important; font-size: 1rem;}

/* EXPANDER */
[data-testid="stExpander"] { border: 1px solid #E2E8F0 !important; border-radius: 12px; background-color: #FFFFFF !important; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
[data-testid="stExpander"] * { color: #0F172A !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def extract_text_from_pdfs(pdf_files):
    combined_text = ""
    for pdf in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf)
            for page in reader.pages:
                combined_text += page.extract_text() + "\n"
        except Exception as e:
            pass
    return combined_text

def generate_pdf_report(report_text, symptoms):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(99, 102, 241)
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

# Sidebar
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

# Tabs
tab1, tab2 = st.tabs(["🩺 Symptom Chat", "📄 Upload Medical Reports"])

# --- TAB 1: CHAT ---
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

# --- TAB 2: MULTIPLE UPLOADS ---
with tab2:
    st.markdown("### 📄 Upload Lab Reports (PDF)")
    st.markdown("<p>Upload one or multiple PDFs (e.g., CBC + LFT). Reason will combine them and provide a full diagnosis.</p>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded.")
        if st.button("Analyze Reports", use_container_width=True):
            if not api_key_input:
                st.error("⚠️ API Key missing.")
                st.stop()
                
            with st.spinner("Extracting text from all PDFs..."):
                extracted = extract_text_from_pdfs(uploaded_files)
                
            if len(extracted.strip()) < 20:
                st.error("Could not read PDF text.")
            else:
                st.success("Text extracted from all files!")
                with st.expander("View Extracted Text"):
                    st.text(extracted[:1500] + "..." if len(extracted) > 1500 else extracted)
                
                with st.spinner("Reasoning through all reports..."):
                    try:
                        client = Groq(api_key=api_key_input)
                        sys_prompt = "You are Reason. Analyze these combined medical reports. Never refer to yourself as AI. FORMAT: ### 📋 Key Findings [list abnormal values] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [explain based on reports] ### 🚨 Urgency Level **[Level]** [explain] ### 🧪 Recommendations * **[Action]:** [advice based on all reports]"
                        res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": extracted}], model="openai/gpt-oss-120b", temperature=0.1).choices[0].message.content
                        st.markdown("---")
                        st.markdown(res)
                        st.session_state.last_report = res
                        st.session_state.last_symptoms = f"Analysis of {len(uploaded_files)} uploaded medical reports."
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# --- PDF DOWNLOAD BUTTON ---
if st.session_state.last_report:
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(st.session_state.last_report, st.session_state.last_symptoms)
    st.download_button("📥 Download Official Report (PDF)", data=pdf_bytes, file_name="Reason_Report.pdf", mime="application/pdf", use_container_width=True)
