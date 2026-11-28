import streamlit as st
import datetime
import html
from io import BytesIO

import pypdf
from fpdf import FPDF
from groq import Groq


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Reason | Clinical AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome to **Reason Clinical AI**. Describe your symptoms "
                "or upload a medical report, and I can help explain the "
                "information for discussion with a qualified healthcare professional."
            ),
        }
    ]

if "report_data" not in st.session_state:
    st.session_state.report_data = None

if "report_source" not in st.session_state:
    st.session_state.report_source = None

if "report_generated_at" not in st.session_state:
    st.session_state.report_generated_at = None


# =========================================================
# API KEY
# =========================================================
try:
    SECRET_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    SECRET_KEY = ""


# =========================================================
# PREMIUM UI — INSPIRED BY THE PROVIDED SAMPLE
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #2878F0;
        --primary-dark: #155DCE;
        --ink: #17345F;
        --muted: #7184A3;
        --line: #E4ECF7;
        --soft-blue: #F1F7FF;
        --surface: #FFFFFF;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #F7FAFF 0%, #F3F7FD 100%);
        color: var(--ink);
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        max-width: 1600px !important;
        padding-top: 1.1rem !important;
        padding-bottom: 2rem !important;
    }

    h1, h2, h3, h4, p, label {
        color: var(--ink);
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E5EDF8;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.2rem 1rem;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif !important;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 4px 4px 22px 4px;
        border-bottom: 1px solid #EDF2F9;
        margin-bottom: 20px;
    }
    .brand-icon {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 22px;
        background: linear-gradient(145deg, #45A0FF, #1765E8);
        box-shadow: 0 7px 18px rgba(40,120,240,.22);
    }
    .brand-name {
        font-size: 18px;
        line-height: 1.2;
        font-weight: 800;
        color: #17345F;
    }
    .brand-tagline {
        font-size: 10px;
        color: #8293AD;
        margin-top: 4px;
    }

    .side-label {
        color: #9AA9BF;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.1px;
        margin: 22px 0 10px 8px;
        text-transform: uppercase;
    }
    .side-note {
        background: linear-gradient(145deg, #F3F8FF, #EAF3FF);
        border: 1px solid #DCEAFF;
        border-radius: 15px;
        padding: 15px;
        margin-top: 26px;
    }
    .side-note-title {
        color: #214A80;
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 7px;
    }
    .side-note-text {
        color: #7186A5;
        font-size: 11px;
        line-height: 1.65;
    }

    /* Top header */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        background: rgba(255,255,255,.88);
        border: 1px solid #E5EDF8;
        border-radius: 16px;
        padding: 13px 19px;
        margin-bottom: 18px;
        box-shadow: 0 5px 18px rgba(32,75,130,.035);
    }
    .topbar-title {
        font-size: 15px;
        font-weight: 800;
        color: #17345F;
    }
    .topbar-subtitle {
        font-size: 11px;
        color: #8293AD;
        margin-top: 4px;
    }
    .topbar-status {
        color: #138B65;
        background: #EAFBF4;
        border: 1px solid #C9F1E1;
        border-radius: 30px;
        padding: 6px 11px;
        font-size: 10px;
        font-weight: 700;
        white-space: nowrap;
    }

    /* Main panels */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #E2EAF5 !important;
        border-radius: 17px !important;
        background: #FFFFFF !important;
        box-shadow: 0 5px 20px rgba(31,70,120,.035);
    }
    .panel-heading {
        font-size: 17px;
        font-weight: 800;
        color: #17345F;
        margin-bottom: 4px;
    }
    .panel-subheading {
        color: #8494AD;
        font-size: 11px;
        line-height: 1.6;
    }
    .section-kicker {
        color: #8295B2;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: .8px;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    /* Chat */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: .45rem .15rem !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        font-size: 13px;
        line-height: 1.75;
        color: #345071;
    }
    [data-testid="stChatInput"] {
        border: 1px solid #DCE7F5 !important;
        border-radius: 15px !important;
        background: #FFFFFF !important;
        box-shadow: 0 5px 18px rgba(35,90,160,.06) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #17345F !important;
        font-size: 13px !important;
    }

    /* Upload */
    [data-testid="stFileUploader"] {
        background: #F5F9FF;
        border: 1px dashed #BBD2F2;
        border-radius: 13px;
        padding: 10px;
    }
    [data-testid="stFileUploader"] * {
        font-size: 11px !important;
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px !important;
        border: 1px solid #2878F0 !important;
        background: linear-gradient(100deg, #3689FA, #1769E8) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        min-height: 42px;
        box-shadow: 0 5px 13px rgba(40,120,240,.14);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #155DCE !important;
        background: #155DCE !important;
        color: white !important;
    }

    /* Report */
    .report-topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 7px;
    }
    .report-chip {
        color: #1878E8;
        background: #EEF6FF;
        border: 1px solid #DCEBFF;
        border-radius: 30px;
        padding: 5px 9px;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: .3px;
    }
    .doctor-chip {
        color: #138B65;
        background: #EAFBF4;
        border: 1px solid #C9F1E1;
        border-radius: 30px;
        padding: 5px 9px;
        font-size: 9px;
        font-weight: 800;
    }
    .report-title {
        font-size: 17px;
        font-weight: 800;
        color: #17345F;
        margin: 9px 0 4px 0;
    }
    .report-meta {
        font-size: 10px;
        color: #8A9BB4;
        border-bottom: 1px solid #EDF2F8;
        padding-bottom: 13px;
        margin-bottom: 12px;
    }
    .empty-report {
        min-height: 390px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: linear-gradient(150deg, #FBFDFF, #F3F8FF);
        border: 1px dashed #C9D9EF;
        border-radius: 15px;
        padding: 25px;
    }
    .empty-icon {
        font-size: 40px;
        margin-bottom: 12px;
    }
    .empty-title {
        font-size: 14px;
        font-weight: 800;
        color: #526D91;
    }
    .empty-copy {
        max-width: 260px;
        font-size: 11px;
        color: #91A1B8;
        line-height: 1.7;
        margin-top: 7px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #E8EEF7;
    }
    .stTabs [data-baseweb="tab"] {
        color: #7186A5;
        font-size: 11px;
        font-weight: 700;
        padding: 8px 7px;
    }
    .stTabs [aria-selected="true"] {
        color: #2878F0 !important;
    }
    .stAlert {
        border-radius: 12px !important;
    }

    @media (max-width: 900px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
        .topbar { padding: 11px 13px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================
def extract_text_from_pdfs(pdf_files):
    """Extract text from uploaded PDF reports."""
    combined_text = ""

    for pdf_file in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf_file)
            pages_text = []

            for page in reader.pages:
                pages_text.append(page.extract_text() or "")

            combined_text += (
                f"\n\n--- Document: {pdf_file.name} ---\n"
                + "\n".join(pages_text)
                + "\n--- End of Document ---\n"
            )
        except Exception as exc:
            combined_text += f"\nCould not read {pdf_file.name}: {exc}\n"

    return combined_text.strip()


def generate_pdf_report(report_text, source_text):
    """Create a downloadable, plain-text clinical discussion report."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 19)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 12, "Reason Clinical AI - Report", ln=True, align="C")

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(100, 116, 139)
    generated = st.session_state.report_generated_at or datetime.datetime.now()
    pdf.cell(
        0,
        7,
        f"Generated: {generated.strftime('%d %b %Y, %I:%M %p')}",
        ln=True,
        align="C",
    )

    pdf.ln(7)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(23, 52, 95)
    pdf.cell(0, 9, "User-provided information", ln=True)

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(45, 55, 72)
    safe_source = (source_text or "Not provided").encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 6, safe_source[:2500])

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(23, 52, 95)
    pdf.cell(0, 9, "AI-generated explanation", ln=True)

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(45, 55, 72)
    safe_report = (
        (report_text or "")
        .replace("**", "")
        .replace("###", "")
        .replace("##", "")
        .replace("#", "")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )
    pdf.multi_cell(0, 6, safe_report)

    pdf.ln(7)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        5,
        "Important: This report is for informational support only. "
        "It is not a medical diagnosis and does not replace examination, "
        "testing, or advice from a qualified healthcare professional.",
    )

    return bytes(pdf.output())


def call_reason(messages, api_key, system_prompt, temperature=0.2):
    """Send recent conversation context to Groq and return the response."""
    client = Groq(api_key=api_key)

    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(messages[-12:])

    response = client.chat.completions.create(
        messages=api_messages,
        model="openai/gpt-oss-120b",
        temperature=temperature,
    )
    return response.choices[0].message.content


def render_chat_message(message):
    avatar = "🧠" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">✚</div>
            <div>
                <div class="brand-name">Reason</div>
                <div class="brand-tagline">Smarter insights. Better care.</div>
            </div>
        </div>
        <div class="side-label">Workspace</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("💬 **AI Assistant**")
    st.markdown("📄 Lab Reports")
    st.markdown("📚 Medical Knowledge")
    st.markdown("⚙️ Settings")

    st.markdown('<div class="side-label">Configuration</div>', unsafe_allow_html=True)

    if SECRET_KEY:
        api_key_input = SECRET_KEY
        st.success("Groq API connected", icon="✅")
    else:
        st.warning("Add your Groq API key to continue.", icon="🔑")
        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="You can add GROQ_API_KEY in Streamlit Cloud Secrets.",
        )

    st.markdown(
        """
        <div class="side-note">
            <div class="side-note-title">🛡️ Patient Safety First</div>
            <div class="side-note-text">
                Reason helps explain health information. It does not replace
                a doctor, emergency service, or professional diagnosis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Reason Clinical AI · Personal health information assistant")


# =========================================================
# TOP HEADER
# =========================================================
st.markdown(
    """
    <div class="topbar">
        <div>
            <div class="topbar-title">Clinical Workspace</div>
            <div class="topbar-subtitle">Understand symptoms and medical reports with clearer explanations.</div>
        </div>
        <div class="topbar-status">● Assistant workspace</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MAIN TWO-PANEL LAYOUT
# =========================================================
col_chat, col_report = st.columns([1.08, 0.92], gap="medium")


# =========================================================
# LEFT: CHAT + UPLOAD
# =========================================================
with col_chat:
    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-heading">✨ Medical AI Assistant</div>
            <div class="panel-subheading">
                Describe your symptoms, upload a lab report, or ask a health question.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Chat history
        chat_area = st.container(height=440, border=False)
        with chat_area:
            for chat_message in st.session_state.messages:
                render_chat_message(chat_message)

        st.markdown('<div class="section-kicker">Upload medical documents</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload PDF lab reports",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="PDF files only. Scanned/image-only PDFs may not contain extractable text.",
        )

        if uploaded_files:
            st.caption(f"{len(uploaded_files)} PDF file(s) selected.")
            if st.button("🔎 Analyze Lab Reports", use_container_width=True):
                if not api_key_input:
                    st.error("Please add your Groq API key first.")
                else:
                    with st.spinner("Reading your PDF report..."):
                        extracted_text = extract_text_from_pdfs(uploaded_files)

                    if not extracted_text.strip():
                        st.error("No readable text was found in the uploaded PDF.")
                    else:
                        report_prompt = """
You are Reason, a careful medical information assistant.
Explain the uploaded laboratory report in plain, cautious language.
Do not claim certainty or present a diagnosis as confirmed.
Do not invent patient details, reference ranges, or test results.
If reference ranges are not shown, say so.
Encourage the user to discuss abnormal results with a qualified clinician.
Mention emergency care only when the supplied information indicates an emergency.

Use this structure:
### Patient Summary
### Key Findings
### Possible Explanations (not a diagnosis)
### Urgency and Safety
### Recommended Next Steps
"""
                        try:
                            with st.spinner("Analyzing the report..."):
                                result = call_reason(
                                    [{"role": "user", "content": extracted_text[:24000]}],
                                    api_key_input,
                                    report_prompt,
                                    temperature=0.1,
                                )

                            st.session_state.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Uploaded {len(uploaded_files)} lab report(s) for analysis.",
                                }
                            )
                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": "Your report has been reviewed. I've added an explanation to the Clinical Report panel. Please use it as a discussion aid with your doctor.",
                                }
                            )
                            st.session_state.report_data = result
                            st.session_state.report_source = extracted_text[:2500]
                            st.session_state.report_generated_at = datetime.datetime.now()
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Report analysis failed: {exc}")


# =========================================================
# RIGHT: CLINICAL REPORT
# =========================================================
with col_report:
    with st.container(border=True):
        st.markdown(
            """
            <div class="report-topline">
                <span class="report-chip">✦ AI GENERATED REPORT</span>
                <span class="doctor-chip">● For Doctor Review</span>
            </div>
            <div class="report-title">Clinical Diagnostic Report</div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.report_data:
            generated = st.session_state.report_generated_at
            generated_label = (
                generated.strftime("%b %d, %Y · %I:%M %p")
                if generated
                else datetime.datetime.now().strftime("%b %d, %Y · %I:%M %p")
            )
            st.markdown(
                f'<div class="report-meta">Generated {html.escape(generated_label)} · Reason Clinical Engine</div>',
                unsafe_allow_html=True,
            )

            tab_summary, tab_full = st.tabs(["Summary", "Full Report"])

            with tab_summary:
                st.info(
                    "This is an AI-generated explanation, not a confirmed diagnosis. "
                    "A qualified clinician should interpret the results in context."
                )
                st.markdown(st.session_state.report_data)

            with tab_full:
                st.markdown(st.session_state.report_data)

            pdf_bytes = generate_pdf_report(
                st.session_state.report_data,
                st.session_state.report_source or "",
            )
            st.download_button(
                "⬇️ Download Full Report",
                data=pdf_bytes,
                file_name="Reason_Clinical_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            if st.button("🗑️ Clear Current Report", use_container_width=True):
                st.session_state.report_data = None
                st.session_state.report_source = None
                st.session_state.report_generated_at = None
                st.rerun()

        else:
            st.markdown(
                """
                <div class="empty-report">
                    <div class="empty-icon">📄</div>
                    <div class="empty-title">No Report Generated Yet</div>
                    <div class="empty-copy">
                        Start a conversation or upload a PDF lab report.
                        Your generated clinical explanation will appear here.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# CHAT INPUT + AI RESPONSE
# =========================================================
prompt = st.chat_input("Type a message or ask a medical question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    if not api_key_input:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Please add your Groq API key in the sidebar before starting an analysis.",
            }
        )
        st.rerun()

    system_prompt = """
You are Reason, a careful medical information assistant.
You help users understand symptoms and medical information in plain language.
You are not a doctor and must not claim to provide a definitive diagnosis.
Never invent medical history, test values, or reference ranges.
Ask concise follow-up questions when important context is missing.
Clearly distinguish possible explanations from confirmed findings.
For urgent or potentially life-threatening symptoms, advise immediate local emergency care.
Do not tell users to stop or change prescribed medication without speaking to their clinician.

Use this response structure when appropriate:
### Patient Summary
### Possible Explanations (not a diagnosis)
### Urgency and Safety
### Recommended Next Steps
"""

    try:
        with st.spinner("Reason is preparing an explanation..."):
            answer = call_reason(
                st.session_state.messages,
                api_key_input,
                system_prompt,
                temperature=0.2,
            )

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.report_data = answer
        st.session_state.report_source = prompt
        st.session_state.report_generated_at = datetime.datetime.now()
        st.rerun()

    except Exception as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"I couldn't complete the request. Please check your API key or connection and try again. Details: {exc}",
            }
        )
        st.rerun()


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div style="text-align:center; color:#9AA9BF; font-size:10px; padding:18px 0 4px 0;">
        Reason Clinical AI · Informational support only · Not a substitute for professional medical care
    </div>
    """,
    unsafe_allow_html=True,
)
