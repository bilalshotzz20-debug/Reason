import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import datetime
import pypdf

# --- PAGE CONFIG ---
st.set_page_config(page_title="Reason | Clinical AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# State Init
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Reason. Please describe your symptoms or upload a medical report to begin."}
    ]
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "report_source" not in st.session_state:
    st.session_state.report_source = None

try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# --- MEDINSIGHT PREMIUM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* GLOBAL */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #F7F9FC !important; color: #1E293B !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 1400px !important; padding-top: 1rem; padding-bottom: 5rem; }

/* Force Visibility */
h1, h2, h3, h4, h5, h6, p, span, div, li, label { color: #1E293B !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; padding-top: 20px;}
[data-testid="stSidebar"] * { color: #1E293B !important; }
.sidebar-logo { font-size: 1.5rem; font-weight: 800; color: #2563EB !important; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;}
.sidebar-nav { display: flex; flex-direction: column; gap: 10px; margin-top: 20px;}
.nav-item { padding: 10px 15px; border-radius: 8px; font-weight: 600; color: #64748B !important; cursor: pointer; transition: 0.2s;}
.nav-item:hover, .nav-item.active { background-color: #EFF6FF !important; color: #2563EB !important; }

/* HEADER */
.top-header { margin-bottom: 20px; }
.top-header h2 { font-size: 1.5rem; font-weight: 800; margin-bottom: 5px; }
.top-header p { color: #64748B !important; font-size: 0.9rem; }

/* CHAT BUBBLES (CUSTOM) */
.chat-bubble-user { background-color: #EFF6FF; border: 1px solid #DBEAFE; padding: 15px 20px; border-radius: 16px 16px 0 16px; margin-bottom: 15px; margin-left: 20%; color: #1E293B !important; font-size: 0.95rem;}
.chat-bubble-ai { background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px 20px; border-radius: 16px 16px 16px 0; margin-bottom: 15px; margin-right: 20%; color: #1E293B !important; font-size: 0.95rem; box-shadow: 0 4px 15px rgba(0,0,0,0.02);}

/* FILE UPLOADER */
[data-testid="stFileUploadDropzone"] { background-color: #F8FAFC !important; border: 2px dashed #CBD5E1 !important; border-radius: 12px !important; padding: 20px !important; }
[data-testid="stFileUploadDropzone"] * { color: #64748B !important; }
[data-testid="stFileUploadDropzone"] button { background-color: #FFFFFF !important; color: #2563EB !important; border: 1px solid #CBD5E1 !important; font-weight: 600 !important;}

/* REPORT PANEL (RIGHT COLUMN) */
.report-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); height: 100%;}
.report-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;}
.report-badge { background-color: #ECFDF5; color: #10B981 !important; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; border: 1px solid #A7F3D0;}
.report-title { font-size: 1.2rem; font-weight: 700; color: #0F172A !important; }
.report-meta { font-size: 0.8rem; color: #64748B !important; margin-bottom: 20px; border-bottom: 1px solid #E2E8F0; padding-bottom: 15px;}
.report-content h3 { font-size: 1rem !important; color: #2563EB !important; margin-top: 15px; margin-bottom: 10px; border-bottom: 1px solid #EFF6FF; padding-bottom: 5px;}
.report-content p, .report-content li { font-size: 0.9rem !important; color: #334155 !important;}

/* BUTTONS */
.stButton > button { background-color: #2563EB !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px; border: none !important; width: 100%;}
.stButton > button:hover { background-color: #1D4ED8 !important; }
.stDownloadButton > button { background-color: #2563EB !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; border: none !important; width: 100%;}

/* INPUT */
[data-testid="stChatInput"] > div { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 30px !important; padding: 5px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;}
[data-testid="stChatInput"] textarea { color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def extract_text_from_pdfs(pdf_files):
    combined_text = ""
    for pdf_file in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                combined_text += page.extract_text() + "\n"
            combined_text += "\n--- End of Document ---\n\n"
        except Exception as e:
            combined_text += f"Error reading {pdf_file.name}: {str(e)}\n"
    return combined_text

def generate_pdf_report(report_text, symptoms):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, "Reason Clinical Diagnostics Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Source Data:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, symptoms.encode('ascii', 'ignore').decode('ascii')[:500] + "...") 
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Diagnostic Assessment:", ln=True)
    pdf.set_font("Arial", size=11)
    clean_text = report_text.replace('**', '').replace('###', '').encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 8, clean_text)
    return bytes(pdf.output())

def check_emergency(text):
    text = text.lower()
    keywords = ["chest pain", "heart attack", "stroke", "cannot breathe", "severe bleeding", "suicidal"]
    return any(k in text for k in keywords)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🧠 Reason</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav"><div class="nav-item active">💬 AI Assistant</div><div class="nav-item">📄 Lab Reports</div><div class="nav-item">⚙️ Settings</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Configuration")
    if SECRET_KEY:
        st.success("✅ API Key connected.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key required.")
        api_key_input = st.text_input("Groq API Key", type="password")
    
    st.markdown("<p style='font-size: 0.75rem; color: #94A3B8; margin-top: 20px;'>Trusted Medical AI. Built for better decisions, with patient safety at the core.</p>", unsafe_allow_html=True)

# --- MAIN LAYOUT (2 COLUMNS) ---
col_chat, col_report = st.columns([1.2, 1], gap="large")

# ==========================================
# LEFT COLUMN: CHAT & UPLOAD
# ==========================================
with col_chat:
    st.markdown('<div class="top-header"><h2>Medical AI Assistant</h2><p>Describe your symptoms, upload lab reports, or ask a medical question.</p></div>', unsafe_allow_html=True)
    
    # Render Chat History
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            
    # PDF Uploader (Custom Styled)
    st.markdown("---")
    st.markdown("#### 📄 Upload Lab Reports")
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files:
        if st.button("Analyze Lab Reports"):
            if not api_key_input:
                st.error("⚠️ API Key missing.")
            else:
                with st.spinner("Extracting data..."):
                    extracted = extract_text_from_pdfs(uploaded_files)
                
                with st.spinner("Reasoning through reports..."):
                    try:
                        client = Groq(api_key=api_key_input)
                        sys_prompt = "You are Reason, an elite medical diagnostician. Analyze these lab reports. Never refer to yourself as AI. FORMAT: ### 📋 Key Findings [List abnormal values] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [explain] **2. [Condition]** *Why it fits:* [explain] ### 🚨 Urgency Level **[Low / Medium / High / CRITICAL]** [explain] ### 🧪 Recommendations * **[Action]:** [advice]"
                        res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": extracted}], model="openai/gpt-oss-120b", temperature=0.1).choices[0].message.content
                        
                        # Save to history and report panel
                        st.session_state.messages.append({"role": "user", "content": f"Uploaded {len(uploaded_files)} Lab Report(s) for analysis."})
                        st.session_state.messages.append({"role": "assistant", "content": "Lab report received. I'll now analyze your symptoms and results and generate a detailed diagnostic report for your doctor."})
                        st.session_state.report_data = res
                        st.session_state.report_source = "Lab Analysis"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==========================================
# RIGHT COLUMN: DIAGNOSTIC REPORT
# ==========================================
with col_report:
    if st.session_state.report_data:
        # Render premium report card
        st.markdown(f"""
        <div class="report-panel">
            <div class="report-header">
                <div class="report-title">Clinical Diagnostic Report</div>
                <div class="report-badge">For Doctor Review</div>
            </div>
            <div class="report-meta">
                Generated on {datetime.datetime.now().strftime('%b %d, %Y')} • Reason Clinical Engine
            </div>
            <div class="report-content">
                {st.session_state.report_data.replace('###', '<h3>').replace('\n', '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download Button
        pdf_bytes = generate_pdf_report(st.session_state.report_data, st.session_state.report_source)
        st.download_button(
            label="📥 Download Full Report",
            data=pdf_bytes,
            file_name="Reason_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        # Empty State
        st.markdown("""
        <div class="report-panel" style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 400px; text-align: center; border: 2px dashed #E2E8F0;">
            <div style="font-size: 3rem; margin-bottom: 15px; opacity: 0.5;">📄</div>
            <div style="font-weight: 700; color: #64748B;">No Report Generated Yet</div>
            <p style="font-size: 0.85rem; color: #94A3B8;">Chat with the AI or upload a lab report to generate a clinical diagnosis.</p>
        </div>
        """, unsafe_allow_html=True)

# --- GLOBAL CHAT INPUT (Bottom) ---
if prompt := st.chat_input("Type your message or ask a medical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # We need to rerun to show the user message instantly in the left column
    st.rerun()

# Process the last message if it's from user and needs AI response
if st.session_state.messages[-1]["role"] == "user" and api_key_input:
    with st.spinner("Thinking..."):
        try:
            client = Groq(api_key=api_key_input)
            sys_prompt = "You are Reason. Never refer to yourself as AI. FORMAT: ### 📋 Patient Summary [1 sentence] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [1 sentence] **2. [Condition]** *Why it fits:* [1 sentence] ### 🚨 Urgency Level **[Level]** [1 sentence] ### 🧪 Recommended Next Steps * **[Test]:** [Why needed] * **[Action]:** [Consult specialist]"
            
            res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": st.session_state.messages[-1]["content"]}], model="openai/gpt-oss-120b", temperature=0.2).choices[0].message.content
            
            # Save to history
            st.session_state.messages.append({"role": "assistant", "content": "I have analyzed your symptoms. A detailed diagnostic report has been generated on the right panel."})
            
            # Push data to Right Column
            st.session_state.report_data = res
            st.session_state.report_source = st.session_state.messages[-2]["content"]
            
            st.rerun() # Refresh to show AI message and Report
        except Exception as e:
            st.error(f"Error: {e}")
