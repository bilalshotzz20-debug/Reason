import streamlit as st
import os
import sqlite3
import json
import datetime
import pypdf
from groq import Groq
from fpdf import FPDF

# ==========================================
# 1. PAGE CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="Reason | Clinical Enterprise", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# Database Init
def init_db():
    conn = sqlite3.connect('reason_clinic.db')
    c = conn.cursor()
    # Patients Table
    c.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, gender TEXT, history TEXT, meds TEXT)''')
    # Reports Table (Memory System)
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, date TEXT, symptoms TEXT, ai_analysis TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Load Settings
def load_settings():
    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            return json.load(f)
    return {"doctor_name": "Dr. Sarah Mitchell", "clinic_name": "Reason Health Clinic", "api_key": ""}

def save_settings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

if "current_patient_id" not in st.session_state:
    st.session_state.current_patient_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "report_data" not in st.session_state:
    st.session_state.report_data = None

try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = st.session_state.settings.get("api_key", "")

# ==========================================
# 2. PREMIUM CSS (LIGHT MODE)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #F7F9FC !important; color: #1E293B !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 1400px !important; padding-top: 1.5rem; padding-bottom: 5rem; }
h1, h2, h3, h4, h5, h6, p, span, div, li, label { color: #1E293B !important; }

[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; padding-top: 20px;}
[data-testid="stSidebar"] * { color: #1E293B !important; }
.sidebar-logo { font-size: 1.8rem; font-weight: 800; color: #2563EB !important; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;}

.top-header h2 { font-size: 1.6rem; font-weight: 800; margin-bottom: 5px; color: #0F172A !important;}
.top-header p { color: #64748B !important; font-size: 0.95rem; }

.chat-bubble-user { background-color: #EFF6FF; border: 1px solid #DBEAFE; padding: 16px 20px; border-radius: 16px 16px 0 16px; margin-bottom: 15px; margin-left: 15%; color: #1E293B !important; font-size: 0.95rem; }
.chat-bubble-ai { background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px 20px; border-radius: 16px 16px 16px 0; margin-bottom: 15px; margin-right: 15%; color: #1E293B !important; font-size: 0.95rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03);}

[data-testid="stFileUploadDropzone"] { background-color: #F8FAFC !important; border: 2px dashed #CBD5E1 !important; border-radius: 12px !important; padding: 20px !important; }
[data-testid="stFileUploadDropzone"] * { color: #64748B !important; }

.report-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
.report-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;}
.report-badge { background-color: #ECFDF5; color: #10B981 !important; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; border: 1px solid #A7F3D0;}
.report-title { font-size: 1.3rem; font-weight: 700; color: #0F172A !important; }
.report-content h3 { font-size: 1.05rem !important; color: #2563EB !important; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #EFF6FF; padding-bottom: 5px;}
.report-content p, .report-content li { font-size: 0.95rem !important; color: #334155 !important; line-height: 1.6;}

.stButton > button { background-color: #2563EB !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px; border: none !important; width: 100%;}
.stDownloadButton > button { background-color: #10B981 !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; border: none !important; width: 100%; padding: 10px 20px;}

[data-testid="stChatInput"] > div { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 30px !important; padding: 5px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;}
[data-testid="stChatInput"] textarea { color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def extract_text_from_pdfs(pdf_files):
    text = ""
    for pdf in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            text += f"Error: {e}\n"
    return text

def get_patient_history(patient_id):
    conn = sqlite3.connect('reason_clinic.db')
    c = conn.cursor()
    c.execute("SELECT date, symptoms, ai_analysis FROM reports WHERE patient_id=? ORDER BY date DESC LIMIT 2", (patient_id,))
    history = c.fetchall()
    conn.close()
    return history

def save_report(patient_id, symptoms, analysis):
    conn = sqlite3.connect('reason_clinic.db')
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO reports (patient_id, date, symptoms, ai_analysis) VALUES (?, ?, ?, ?)", (patient_id, date, symptoms, analysis))
    conn.commit()
    conn.close()

def generate_pdf_report(report_text, patient_name, doctor_name, clinic_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, f"{clinic_name}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Doctor: {doctor_name} | Patient: {patient_name} | Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    clean_text = report_text.replace('**', '').replace('###', '').encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 8, clean_text)
    return bytes(pdf.output())

# ==========================================
# 4. SIDEBAR NAVIGATION & SETTINGS
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🧠 Reason</div>', unsafe_allow_html=True)
    
    # Patient Selection
    st.markdown("### 👤 Patient Directory")
    conn = sqlite3.connect('reason_clinic.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM patients")
    patients = c.fetchall()
    conn.close()
    
    patient_options = {p[1]: p[0] for p in patients}
    selected_patient_name = st.selectbox("Select Active Patient", ["-- New Patient --"] + list(patient_options.keys()))
    
    if selected_patient_name != "-- New Patient --":
        st.session_state.current_patient_id = patient_options[selected_patient_name]
    else:
        st.session_state.current_patient_id = None

    # Add New Patient Form
    with st.expander("➕ Add New Patient"):
        new_name = st.text_input("Name")
        new_age = st.number_input("Age", 1, 120, 30)
        new_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        new_history = st.text_area("Medical History (Optional)")
        new_meds = st.text_area("Current Medications (Optional)")
        if st.button("Save Patient"):
            if new_name:
                conn = sqlite3.connect('reason_clinic.db')
                c = conn.cursor()
                c.execute("INSERT INTO patients (name, age, gender, history, meds) VALUES (?, ?, ?, ?, ?)", (new_name, new_age, new_gender, new_history, new_meds))
                conn.commit()
                conn.close()
                st.success(f"Patient {new_name} added!")
                st.rerun()

    st.divider()
    
    # System Settings
    with st.expander("⚙️ System Settings"):
        doc_name = st.text_input("Doctor Name", value=st.session_state.settings.get("doctor_name", "Dr. Sarah Mitchell"))
        clinic_name = st.text_input("Clinic Name", value=st.session_state.settings.get("clinic_name", "Reason Health Clinic"))
        api_key = st.text_input("Groq API Key", value=st.session_state.settings.get("api_key", ""), type="password")
        
        if st.button("Save Settings"):
            st.session_state.settings = {"doctor_name": doc_name, "clinic_name": clinic_name, "api_key": api_key}
            save_settings(st.session_state.settings)
            st.success("Settings Saved!")
            st.rerun()

# ==========================================
# 5. MAIN UI (3-COLUMN)
# ==========================================
col_chat, col_report = st.columns([1.2, 1], gap="large")

with col_chat:
    st.markdown('<div class="top-header"><h2>Medical AI Assistant</h2><p>Select a patient from the sidebar to view their memory and start analysis.</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.current_patient_id:
        st.info("Please select or add a patient in the sidebar to begin.")
    else:
        # Show Patient History (Memory System)
        history = get_patient_history(st.session_state.current_patient_id)
        if history:
            st.markdown("#### 🧠 Patient Memory (Previous Visits)")
            for h in history:
                with st.expander(f"Visit on {h[0]} - {h[1][:50]}..."):
                    st.markdown(h[2])

        # Chat Interface
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)
        
        # File Uploader
        st.markdown("#### 📄 Upload Lab Reports")
        uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        
        if uploaded_files and st.button("Analyze Reports"):
            if not SECRET_KEY:
                st.error("API Key missing in Settings.")
            else:
                with st.spinner("Extracting and reasoning with patient memory..."):
                    extracted = extract_text_from_pdfs(uploaded_files)
                    
                    # Build Context from Memory
                    context = ""
                    if history:
                        context = "PAST MEDICAL REPORTS:\n"
                        for h in history:
                            context += f"Date: {h[0]}\nSymptoms: {h[1]}\nAnalysis: {h[2]}\n\n"

                    client = Groq(api_key=SECRET_KEY)
                    sys_prompt = f"""
                    You are Reason, an elite clinical diagnostician.
                    {context}
                    
                    NEW REPORT DATA:
                    {extracted}
                    
                    Based on the past history and new data, provide a Longitudinal Analysis (Trend Analysis). 
                    FORMAT EXACTLY LIKE THIS:
                    ### 📋 SOAP Note
                    **Subjective:** [Patient symptoms]
                    **Objective:** [Lab findings]
                    **Assessment:** [Diagnosis / Trend comparison with past]
                    **Plan:** [Next steps]
                    """
                    
                    res = client.chat.completions.create(
                        messages=[{"role": "system", "content": sys_prompt}],
                        model="openai/gpt-oss-120b", temperature=0.1
                    ).choices[0].message.content
                    
                    save_report(st.session_state.current_patient_id, "Uploaded Lab PDF", res)
                    st.session_state.report_data = res
                    st.session_state.messages.append({"role": "user", "content": "Uploaded Lab Reports for Analysis."})
                    st.session_state.messages.append({"role": "assistant", "content": "Analysis complete. See the clinical report on the right."})
                    st.rerun()

with col_report:
    if st.session_state.report_data:
        formatted_report = st.session_state.report_data.replace('###', '<h3>').replace('**', '<b>').replace('\n', '<br>').replace('</b>', '</b>')
        
        st.markdown(f"""
        <div class="report-panel">
            <div class="report-header">
                <div class="report-title">Clinical Diagnostic Report</div>
                <div class="report-badge">SOAP Format</div>
            </div>
            <div class="report-content">
                {formatted_report}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generate_pdf_report(st.session_state.report_data, selected_patient_name, st.session_state.settings['doctor_name'], st.session_state.settings['clinic_name'])
        st.download_button("📥 Download Official PDF Report", data=pdf_bytes, file_name=f"{selected_patient_name}_Report.pdf", mime="application/pdf")
    else:
        st.markdown("""
        <div class="report-panel" style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 500px; text-align: center; border: 2px dashed #E2E8F0;">
            <div style="font-size: 3rem; margin-bottom: 15px; opacity: 0.5;">📄</div>
            <div style="font-weight: 700; color: #64748B; font-size: 1.1rem;">No Report Yet</div>
            <p style="font-size: 0.9rem; color: #94A3B8;">Upload a report or chat to generate a SOAP Note.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. CHAT INPUT
# ==========================================
if st.session_state.current_patient_id:
    if prompt := st.chat_input("Describe symptoms or ask a question..."):
        if not SECRET_KEY:
            st.error("API Key missing in Settings.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("Reasoning..."):
                # Fetch Memory
                history = get_patient_history(st.session_state.current_patient_id)
                context = ""
                if history:
                    context = "PAST MEDICAL REPORTS:\n"
                    for h in history:
                        context += f"Date: {h[0]}\nSymptoms: {h[1]}\nAnalysis: {h[2]}\n\n"

                client = Groq(api_key=SECRET_KEY)
                sys_prompt = f"""
                You are Reason, an elite clinical diagnostician.
                {context}
                
                Analyze the new symptoms: {prompt}
                
                FORMAT EXACTLY LIKE THIS:
                ### 📋 SOAP Note
                **Subjective:** [Patient symptoms]
                **Objective:** [Clinical observations]
                **Assessment:** [Diagnosis / Trend comparison with past]
                **Plan:** [Next steps / Medications]
                """
                
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_prompt}],
                    model="openai/gpt-oss-120b", temperature=0.2
                ).choices[0].message.content
                
                save_report(st.session_state.current_patient_id, prompt, res)
                st.session_state.report_data = res
                st.session_state.messages.append({"role": "assistant", "content": "Analysis complete. A SOAP note has been generated on the right panel."})
                st.rerun()
