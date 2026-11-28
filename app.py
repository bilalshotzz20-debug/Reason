import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import datetime
import pypdf

# ==========================================
# 1. PAGE CONFIG & STATE MANAGEMENT
# ==========================================
st.set_page_config(page_title="Reason | Clinical AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Reason. Please describe your symptoms or upload a medical report to begin."}
    ]
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "report_source" not in st.session_state:
    st.session_state.report_source = None

# Fetch API Key
try:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
except:
    SECRET_KEY = None

# ==========================================
# 2. ULTRA PREMIUM CSS (FORCED LIGHT MODE)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Global App Settings */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #F7F9FC !important; color: #1E293B !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 1400px !important; padding-top: 1.5rem; padding-bottom: 5rem; }

/* Force Visibility of All Text */
h1, h2, h3, h4, h5, h6, p, span, div, li, label { color: #1E293B !important; }

/* Sidebar Styling */
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; padding-top: 20px;}
[data-testid="stSidebar"] * { color: #1E293B !important; }
.sidebar-logo { font-size: 1.8rem; font-weight: 800; color: #2563EB !important; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;}
.sidebar-nav { display: flex; flex-direction: column; gap: 10px; margin-top: 20px;}
.nav-item { padding: 12px 18px; border-radius: 8px; font-weight: 600; color: #64748B !important; cursor: pointer; transition: 0.2s; font-size: 1rem;}
.nav-item:hover, .nav-item.active { background-color: #EFF6FF !important; color: #2563EB !important; }

/* Top Header */
.top-header h2 { font-size: 1.6rem; font-weight: 800; margin-bottom: 5px; color: #0F172A !important;}
.top-header p { color: #64748B !important; font-size: 0.95rem; }

/* Custom Chat Bubbles */
.chat-bubble-user { background-color: #EFF6FF; border: 1px solid #DBEAFE; padding: 16px 20px; border-radius: 16px 16px 0 16px; margin-bottom: 15px; margin-left: 15%; color: #1E293B !important; font-size: 0.95rem; box-shadow: 0 2px 10px rgba(0,0,0,0.02);}
.chat-bubble-ai { background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px 20px; border-radius: 16px 16px 16px 0; margin-bottom: 15px; margin-right: 15%; color: #1E293B !important; font-size: 0.95rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03);}

/* File Uploader */
[data-testid="stFileUploadDropzone"] { background-color: #F8FAFC !important; border: 2px dashed #CBD5E1 !important; border-radius: 12px !important; padding: 20px !important; }
[data-testid="stFileUploadDropzone"] * { color: #64748B !important; }
[data-testid="stFileUploadDropzone"] button { background-color: #FFFFFF !important; color: #2563EB !important; border: 1px solid #CBD5E1 !important; font-weight: 600 !important; border-radius: 6px;}

/* Right Panel: Report Card */
.report-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); height: 100%;}
.report-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;}
.report-badge { background-color: #ECFDF5; color: #10B981 !important; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; border: 1px solid #A7F3D0;}
.report-title { font-size: 1.3rem; font-weight: 700; color: #0F172A !important; }
.report-meta { font-size: 0.85rem; color: #64748B !important; margin-bottom: 20px; border-bottom: 1px solid #E2E8F0; padding-bottom: 15px;}
.report-content h3 { font-size: 1.05rem !important; color: #2563EB !important; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #EFF6FF; padding-bottom: 5px;}
.report-content p, .report-content li { font-size: 0.95rem !important; color: #334155 !important; line-height: 1.6;}

/* Buttons */
.stButton > button { background-color: #2563EB !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px; border: none !important; width: 100%; transition: 0.3s;}
.stButton > button:hover { background-color: #1D4ED8 !important; }
.stDownloadButton > button { background-color: #2563EB !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; border: none !important; width: 100%; padding: 10px 20px;}

/* Chat Input */
[data-testid="stChatInput"] { background-color: #F7F9FC !important; }
[data-testid="stChatInput"] > div { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 30px !important; padding: 5px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;}
[data-testid="stChatInput"] textarea { color: #1E293B !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #94A3B8 !important; }

/* Emergency Banner */
.emergency-banner { background-color: #FEF2F2; border-left: 6px solid #EF4444; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; margin-top: 10px;}
.emergency-banner * { color: #991B1B !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
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

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🧠 Reason</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav"><div class="nav-item active">💬 AI Assistant</div><div class="nav-item">📄 Lab Reports</div><div class="nav-item">⚙️ Settings</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Configuration")
    if SECRET_KEY:
        st.success("✅ API Key connected.")
        api_key_input = SECRET_KEY
    else:
        st.warning("⚠️ API Key required.")
        api_key_input = st.text_input("Groq API Key", type="password")
    
    st.markdown("<p style='font-size: 0.75rem; color: #94A3B8; margin-top: 20px;'>Trusted Medical AI. Built for better decisions, with patient safety at the core.</p>", unsafe_allow_html=True)

# ==========================================
# 5. MAIN UI (3-COLUMN LAYOUT)
# ==========================================
col_chat, col_report = st.columns([1.2, 1], gap="large")

# --- LEFT COLUMN: CHAT & UPLOAD ---
with col_chat:
    st.markdown('<div class="top-header"><h2>Medical AI Assistant</h2><p>Describe your symptoms, upload lab reports, or ask a medical question.</p></div>', unsafe_allow_html=True)
    
    # Render Chat History
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            # Render AI markdown properly inside bubble
            formatted_content = msg["content"].replace("\n", "<br>").replace("###", "<b>").replace("**", "")
            st.markdown(f'<div class="chat-bubble-ai">{formatted_content}</div>', unsafe_allow_html=True)
            
    # PDF Uploader
    st.markdown("---")
    st.markdown("#### 📄 Upload Lab Reports")
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files:
        if st.button("Analyze Lab Reports"):
            if not api_key_input:
                st.error("⚠️ API Key missing.")
            else:
                with st.spinner("Extracting data from PDFs..."):
                    extracted = extract_text_from_pdfs(uploaded_files)
                
                with st.spinner("Reasoning through medical data..."):
                    try:
                        client = Groq(api_key=api_key_input)
                        sys_prompt = "You are Reason. Analyze these lab reports. FORMAT: ### 📋 Key Findings [List abnormal values] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [explain] **2. [Condition]** *Why it fits:* [explain] ### 🚨 Urgency Level **[Low / Medium / High / CRITICAL]** [explain] ### 🧪 Recommendations * **[Action]:** [advice]"
                        res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": extracted}], model="openai/gpt-oss-120b", temperature=0.1).choices[0].message.content
                        
                        # Update states
                        st.session_state.messages.append({"role": "user", "content": f"Uploaded {len(uploaded_files)} Lab Report(s) for analysis."})
                        st.session_state.messages.append({"role": "assistant", "content": "Lab report received. Diagnostic report generated on the right panel."})
                        st.session_state.report_data = res
                        st.session_state.report_source = "Lab Analysis"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- RIGHT COLUMN: DIAGNOSTIC REPORT ---
with col_report:
    if st.session_state.report_data:
        # Display Generated Report
        formatted_report = st.session_state.report_data.replace('###', '<h3>').replace('**', '').replace('\n', '<br>')
        
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
                {formatted_report}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download Button
        pdf_bytes = generate_pdf_report(st.session_state.report_data, st.session_state.report_source)
        st.download_button(
            label="📥 Download Full Report (PDF)",
            data=pdf_bytes,
            file_name="Reason_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        # Empty State
        st.markdown("""
        <div class="report-panel" style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 500px; text-align: center; border: 2px dashed #E2E8F0;">
            <div style="font-size: 3rem; margin-bottom: 15px; opacity: 0.5;">📄</div>
            <div style="font-weight: 700; color: #64748B; font-size: 1.1rem;">No Report Generated Yet</div>
            <p style="font-size: 0.9rem; color: #94A3B8; max-width: 80%;">Chat with the AI or upload a lab report to generate a clinical diagnosis.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. CHAT INPUT LOGIC (BOTTOM)
# ==========================================
if prompt := st.chat_input("Type your message or ask a medical question..."):
    # 1. Save User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Emergency Check
    if check_emergency(prompt):
        st.session_state.messages.append({"role": "assistant", "content": "🚨 CALL EMERGENCY SERVICES (1122 / 911) IMMEDIATELY. Do not drive yourself."})
        st.rerun()
    
    # 3. AI Generation
    if api_key_input:
        with st.spinner("Reasoning..."):
            try:
                client = Groq(api_key=api_key_input)
                sys_prompt = "You are Reason. Analyze symptoms. FORMAT: ### 📋 Patient Summary [1 sentence] ### 🦠 Top Possible Conditions **1. [Condition]** *Why it fits:* [1 sentence] **2. [Condition]** *Why it fits:* [1 sentence] ### 🚨 Urgency Level **[Level]** [1 sentence] ### 🧪 Recommended Next Steps * **[Test]:** [Why needed] * **[Action]:** [Consult specialist]"
                
                res = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}], model="openai/gpt-oss-120b", temperature=0.2).choices[0].message.content
                
                # Save AI Response to Chat
                st.session_state.messages.append({"role": "assistant", "content": "I have analyzed your symptoms. A detailed clinical report is available on the right panel."})
                
                # Save Data to Right Column
                st.session_state.report_data = res
                st.session_state.report_source = prompt
                
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("⚠️ API Key missing. Please check the sidebar.")
