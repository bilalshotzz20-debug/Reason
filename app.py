
import streamlit as st
import datetime
import html
import io
import re

from groq import Groq
from fpdf import FPDF
import pypdf


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Reason | Clinical AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome to Reason Clinical AI. Describe your symptoms "
                "or upload a medical report to begin."
            )
        }
    ]

if "report_data" not in st.session_state:
    st.session_state.report_data = None

if "report_source" not in st.session_state:
    st.session_state.report_source = ""

if "last_processed_prompt" not in st.session_state:
    st.session_state.last_processed_prompt = None


# =========================================================
# API KEY
# =========================================================

try:
    SECRET_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    SECRET_KEY = ""

# =========================================================
# ANIMATED CLINICAL DESIGN SYSTEM
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #2563EB;
    --primary-dark: #1D4ED8;
    --navy: #0F172A;
    --text: #334155;
    --muted: #64748B;
    --border: #E2E8F0;
    --surface: #FFFFFF;
    --background: #F4F7FB;
    --soft-blue: #EFF6FF;
}

/* GLOBAL */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: var(--background) !important;
    color: var(--text) !important;
    animation: pageFade 0.8s ease both;
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1500px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 5rem !important;
}

/* ANIMATION KEYFRAMES */

@keyframes pageFade {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-25px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(25px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes floatLogo {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-6px);
    }
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.12);
    }
    50% {
        box-shadow: 0 0 0 7px rgba(37, 99, 235, 0);
    }
}

@keyframes shimmer {
    0% {
        background-position: -200% center;
    }
    100% {
        background-position: 200% center;
    }
}

@keyframes reportReveal {
    from {
        opacity: 0;
        transform: translateY(18px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes softGlow {
    0%, 100% {
        border-color: #DBEAFE;
    }
    50% {
        border-color: #93C5FD;
    }
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid var(--border);
    animation: slideInLeft 0.7s ease both;
}

[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 15px 5px 25px 5px;
}

.sidebar-icon {
    width: 43px;
    height: 43px;
    background: linear-gradient(135deg, #2563EB, #60A5FA);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
    animation: floatLogo 3s ease-in-out infinite;
    box-shadow: 0 7px 20px rgba(37, 99, 235, 0.2);
}

.sidebar-brand-name {
    font-size: 23px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -1px;
}

.sidebar-brand-sub {
    font-size: 10px;
    color: #64748B;
    letter-spacing: 2px;
    font-weight: 700;
}

/* HEADER */

.main-heading {
    font-size: 29px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -1px;
    margin-bottom: 5px;
    animation: slideInRight 0.7s ease both;
}

.main-subheading {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 25px;
    animation: pageFade 1s ease both;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 12px;
    background: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    animation: pulse 3s infinite;
}

/* SECTION HEADERS */

.section-title {
    font-size: 17px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 5px;
}

.section-description {
    color: #64748B;
    font-size: 12px;
    margin-bottom: 17px;
}

/* CARDS */

.clinical-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 5px 20px rgba(15, 23, 42, 0.035);
    animation: reportReveal 0.7s ease both;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.clinical-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
}

/* CHAT */

.chat-bubble-user {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
    border: 1px solid #BFDBFE;
    padding: 15px 18px;
    border-radius: 17px 17px 4px 17px;
    margin: 12px 0 12px 12%;
    color: #1E3A8A;
    font-size: 13px;
    line-height: 1.7;
    animation: slideInRight 0.45s ease both;
    overflow-wrap: anywhere;
}

.chat-bubble-ai {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    padding: 16px 18px;
    border-radius: 17px 17px 17px 4px;
    margin: 12px 12% 12px 0;
    color: #334155;
    font-size: 13px;
    line-height: 1.7;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.025);
    animation: slideInLeft 0.45s ease both;
    overflow-wrap: anywhere;
}

/* REPORT PANEL */

.report-panel {
    background: #FFFFFF;
    border: 1px solid #DBEAFE;
    border-radius: 20px;
    padding: 23px;
    box-shadow: 0 10px 35px rgba(37, 99, 235, 0.055);
    animation: reportReveal 0.7s ease both;
}

.report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
}

.report-title {
    font-size: 18px;
    font-weight: 800;
    color: #0F172A;
}

.report-badge {
    background: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    border-radius: 30px;
    padding: 6px 11px;
    font-size: 10px;
    font-weight: 800;
    animation: pulse 3s infinite;
}

.report-meta {
    font-size: 11px;
    color: #64748B;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 15px;
    margin-bottom: 15px;
}

.report-content {
    color: #334155;
    font-size: 13px;
    line-height: 1.8;
    overflow-wrap: anywhere;
}

.report-content h1,
.report-content h2,
.report-content h3 {
    color: #1D4ED8 !important;
    font-size: 15px !important;
    margin-top: 20px !important;
    padding-bottom: 7px;
    border-bottom: 1px solid #DBEAFE;
}

.report-content p,
.report-content li {
    color: #334155 !important;
    font-size: 13px !important;
}

.report-content strong {
    color: #0F172A !important;
}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px !important;
    min-height: 43px;
    font-weight: 700 !important;
    border: 1px solid #2563EB !important;
    background: linear-gradient(110deg, #2563EB, #1D4ED8, #3B82F6) !important;
    background-size: 200% auto !important;
    color: #FFFFFF !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 9px 22px rgba(37, 99, 235, 0.25);
    background-position: right center !important;
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid #CBD5E1 !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    border-radius: 20px !important;
}

[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 18px !important;
    box-shadow: 0 5px 20px rgba(37, 99, 235, 0.07) !important;
    transition: all 0.3s ease;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.09) !important;
}

/* FILE UPLOADER */

[data-testid="stFileUploadDropzone"] {
    background: #F8FAFC !important;
    border: 2px dashed #93C5FD !important;
    border-radius: 14px !important;
    transition: all 0.3s ease;
}

[data-testid="stFileUploadDropzone"]:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
    animation: softGlow 2s infinite;
}

[data-testid="stFileUploadDropzone"] * {
    color: #475569 !important;
}

/* DIVIDERS */

hr {
    border-color: #E2E8F0 !important;
}

/* EMPTY STATE */

.empty-state {
    min-height: 350px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: #FFFFFF;
    border: 2px dashed #BFDBFE;
    border-radius: 20px;
    padding: 25px;
    animation: reportReveal 0.8s ease both;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 15px;
    animation: floatLogo 3s ease-in-out infinite;
}

.empty-title {
    font-size: 16px;
    font-weight: 800;
    color: #334155;
}

.empty-description {
    font-size: 12px;
    color: #64748B;
    max-width: 260px;
    line-height: 1.7;
}

/* FOOTER */

.app-footer {
    text-align: center;
    padding: 20px 5px;
    color: #94A3B8;
    font-size: 10px;
    letter-spacing: 0.5px;
}

/* ACCESSIBILITY */

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* MOBILE */

@media (max-width: 768px) {
    .main-heading {
        font-size: 23px;
    }

    .chat-bubble-user {
        margin-left: 4%;
    }

    .chat-bubble-ai {
        margin-right: 4%;
    }

    .clinical-card,
    .report-panel {
        padding: 16px;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_text_from_pdfs(pdf_files):
    combined_text = []

    for pdf_file in pdf_files:
        try:
            pdf_file.seek(0)
            reader = pypdf.PdfReader(pdf_file)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    combined_text.append(
                        f"Could not open encrypted PDF: {pdf_file.name}"
                    )
                    continue

            for page_number, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                combined_text.append(
                    f"\n--- {pdf_file.name} | Page {page_number} ---\n"
                    f"{page_text}"
                )

        except Exception as error:
            combined_text.append(
                f"\nError reading {pdf_file.name}: {str(error)}"
            )

    return "\n".join(combined_text).strip()


# =========================================================
# PDF REPORT GENERATOR
# =========================================================

def generate_pdf_report(report_text, source_text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 19)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(
        0, 12,
        "REASON CLINICAL REPORT",
        ln=True,
        align="C"
    )

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(
        0, 8,
        datetime.datetime.now().strftime(
            "Generated: %d %B %Y | %H:%M"
        ),
        ln=True,
        align="C"
    )

    pdf.ln(8)

    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 9, "SOURCE INFORMATION", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(51, 65, 85)

    safe_source = (
        str(source_text)
        .encode("latin-1", "replace")
        .decode("latin-1")
    )

    pdf.multi_cell(0, 7, safe_source[:3000] or "Not provided")

    pdf.ln(6)

    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 9, "CLINICAL ASSESSMENT", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(51, 65, 85)

    clean_report = re.sub(
        r"[*#`]",
        "",
        str(report_text)
    )

    clean_report = (
        clean_report
        .encode("latin-1", "replace")
        .decode("latin-1")
    )

    pdf.multi_cell(0, 7, clean_report)

    pdf.ln(8)

    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(100, 116, 139)

    pdf.multi_cell(
        0,
        5,
        "Important: This report is generated for informational "
        "purposes only. It is not a confirmed diagnosis and "
        "must be reviewed by a qualified healthcare professional."
    )

    output = pdf.output()

    if isinstance(output, str):
        return output.encode("latin-1")

    return bytes(output)


# =========================================================
# GROQ CLINICAL ANALYSIS
# =========================================================

SYSTEM_PROMPT = """
You are Reason, a clinical information assistant.

Your job is to help users understand symptoms and medical reports.
You must be careful, evidence-aware, and safety-focused.

IMPORTANT RULES:
1. Never claim a confirmed diagnosis.
2. Explain that possible conditions are not definitive diagnoses.
3. Never invent laboratory values, symptoms, or medical history.
4. If information is missing, clearly say so.
5. Explain abnormal lab values using the reference ranges provided.
6. Do not recommend prescription medicines or dosages.
7. Encourage consultation with a qualified healthcare professional.
8. If emergency warning signs are described, clearly advise urgent
   medical evaluation.

Use this report format:

### Patient Summary
Brief summary of the information provided.

### Key Findings
List important symptoms, values, and abnormalities.
Mention when reference ranges are unavailable.

### Possible Conditions
List reasonable possibilities with explanations.
Clearly state that these are not confirmed diagnoses.

### Urgency Level
Low / Moderate / High / Emergency.
Explain the reasoning and limitations.

### Recommended Next Steps
Suggest appropriate questions, tests to discuss with a clinician,
and practical next steps.

### Important Disclaimer
State that this is informational support, not a substitute
for professional medical diagnosis or treatment.

Use clear, simple English.
"""


def analyze_with_groq(api_key, user_content, history=None):
    client = Groq(api_key=api_key)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if history:
        messages.extend(history[-8:])

    messages.append({
        "role": "user",
        "content": user_content
    })

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.2,
        max_tokens=2500
    )

    return response.choices[0].message.content


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-icon">🧠</div>
        <div>
            <div class="sidebar-brand-name">Reason</div>
            <div class="sidebar-brand-sub">CLINICAL INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 💬 Workspace")

    st.markdown(
        "<div style='background:#EFF6FF;padding:12px;"
        "border-radius:10px;color:#1D4ED8;font-weight:700;"
        "font-size:13px;'>● Clinical AI Assistant</div>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### ⚙️ Configuration")

    if SECRET_KEY:
        api_key_input = SECRET_KEY
        st.success("Groq API connected")
    else:
        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="Enter your Groq API key",
            help="Your key is used to connect to Groq."
        )

        if api_key_input:
            st.success("API key entered")

    st.markdown("---")

    st.markdown("### 📊 Session")

    st.metric(
        "Messages",
        len(st.session_state.messages)
    )

    if st.session_state.report_data:
        st.success("Clinical report available")
    else:
        st.info("No report generated yet")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Welcome to Reason Clinical AI. "
                    "Describe your symptoms or upload a medical report."
                )
            }
        ]
        st.session_state.report_data = None
        st.session_state.report_source = ""
        st.session_state.last_processed_prompt = None
        st.rerun()

    st.markdown("---")

    st.markdown("""
    <div style="font-size:11px;color:#64748B;line-height:1.8;">
        <b>REASON CLINICAL AI</b><br>
        Designed to support better medical understanding.<br><br>
        Patient safety comes first.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN HEADER
# =========================================================

header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        '<div class="main-heading">Clinical Intelligence Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">'
        'Understand symptoms, review lab reports, and explore '
        'health information with clinical AI support.'
        '</div>',
        unsafe_allow_html=True
    )

with header_right:
    st.markdown(
        '<div style="text-align:right;padding-top:8px;">'
        '<span class="status-pill">● SYSTEM READY</span>'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# MAIN TWO-COLUMN LAYOUT
# =========================================================

col_chat, col_report = st.columns(
    [1.12, 0.88],
    gap="large"
)


# =========================================================
# LEFT: CHAT AND PDF UPLOAD
# =========================================================

with col_chat:

    st.markdown(
        '<div class="section-title">💬 Medical AI Assistant</div>'
        '<div class="section-description">'
        'Discuss symptoms or ask questions about your health.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="clinical-card">', unsafe_allow_html=True)

    for message in st.session_state.messages:

        safe_content = html.escape(
            str(message["content"])
        ).replace("\n", "<br>")

        if message["role"] == "user":
            st.markdown(
                f'<div class="chat-bubble-user">'
                f'<b>You</b><br>{safe_content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-bubble-ai">'
                f'<b>🧠 Reason</b><br>{safe_content}</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">📄 Lab Report Analysis</div>'
        '<div class="section-description">'
        'Upload PDF laboratory reports for structured analysis.'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Upload medical PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload more than one PDF."
    )

    if st.button(
        "🔬 Analyze Lab Reports",
        use_container_width=True
    ):

        if not api_key_input:
            st.error("Please enter your Groq API key in the sidebar.")

        elif not uploaded_files:
            st.warning("Please upload at least one PDF file.")

        else:
            with st.spinner("Extracting PDF information..."):
                extracted_text = extract_text_from_pdfs(uploaded_files)

            if not extracted_text.strip():
                st.error(
                    "No readable text was found. "
                    "The PDF may be scanned or image-based."
                )

            else:
                with st.spinner("Analyzing clinical information..."):

                    try:
                        report = analyze_with_groq(
                            api_key_input,
                            (
                                "Analyze the following uploaded medical "
                                "report information carefully. Do not "
                                "invent missing values.\n\n"
                                + extracted_text[:18000]
                            )
                        )

                        st.session_state.messages.append({
                            "role": "user",
                            "content": (
                                f"Uploaded {len(uploaded_files)} "
                                "medical PDF report(s) for analysis."
                            )
                        })

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": (
                                "Your uploaded report has been analyzed. "
                                "Please review the clinical report panel."
                            )
                        })

                        st.session_state.report_data = report
                        st.session_state.report_source = (
                            "Uploaded laboratory report(s): "
                            + ", ".join(
                                file.name for file in uploaded_files
                            )
                        )

                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"Analysis failed: {str(error)}"
                        )


# =========================================================
# RIGHT: CLINICAL REPORT PANEL
# =========================================================

with col_report:

    st.markdown(
        '<div class="section-title">📋 Clinical Report</div>'
        '<div class="section-description">'
        'Your latest AI-generated clinical assessment.'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.report_data:

        st.markdown("""
        <div class="report-panel">
            <div class="report-header">
                <div class="report-title">
                    Clinical Assessment
                </div>
                <div class="report-badge">
                    FOR DOCTOR REVIEW
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="report-meta">'
            + datetime.datetime.now().strftime(
                "Generated on %d %B %Y at %H:%M"
            )
            + ' · Reason Clinical Engine'
            + '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="report-content">',
            unsafe_allow_html=True
        )

        st.markdown(st.session_state.report_data)

        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        try:
            pdf_bytes = generate_pdf_report(
                st.session_state.report_data,
                st.session_state.report_source
            )

            st.download_button(
                label="📥 Download Clinical PDF Report",
                data=pdf_bytes,
                file_name="Reason_Clinical_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as error:
            st.error(f"PDF generation error: {str(error)}")

    else:

        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <div class="empty-title">
                No Clinical Report Yet
            </div>
            <div class="empty-description">
                Start a conversation or upload a laboratory report.
                Your clinical assessment will appear here.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:#EFF6FF;
        border:1px solid #BFDBFE;
        padding:14px;
        border-radius:13px;
        font-size:11px;
        line-height:1.7;
        color:#1E40AF;
    ">
        <b>⚕️ Medical Safety Notice</b><br>
        Reason provides informational support only. It does not
        replace a qualified doctor, clinical examination, or
        emergency medical care.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# GLOBAL CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Describe your symptoms or ask a medical question..."
)

if prompt:

    if not api_key_input:
        st.error(
            "Please add your Groq API key in the sidebar first."
        )

    else:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.spinner("Reason is reviewing your message..."):

            try:
                # Use recent conversation for context.
                history = [
                    {
                        "role": item["role"],
                        "content": item["content"]
                    }
                    for item in st.session_state.messages[:-1]
                    if item["role"] in ("user", "assistant")
                ]

                response = analyze_with_groq(
                    api_key_input,
                    prompt,
                    history=history
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "Your clinical information has been reviewed. "
                        "See the assessment on the right."
                    )
                })

                st.session_state.report_data = response
                st.session_state.report_source = prompt

                st.rerun()

            except Exception as error:
                st.error(
                    f"Something went wrong: {str(error)}"
                )


# =========================================================
# FOOTER
# =========================================================

