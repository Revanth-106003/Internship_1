"""
app.py
------
AI Document Comparison Assistant
Streamlit Web Application featuring a polished, modern AI SaaS interface,
robust dual-PDF upload workspace, live validation, Gemini-powered analysis,
interactive results dashboard, and multi-format report exports.
"""

import os
import sys
import time
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Ensure local modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_reader import (
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_MAX_PAGE_COUNT,
    ExtractedDocument,
    extract_text_from_pdf,
    get_configured_limits,
)
from comparison import (
    DEFAULT_MODEL,
    ComparisonResult,
    GeminiComparisonError,
    InvalidApiKeyError,
    MalformedResponseError,
    MissingApiKeyError,
    ModelUnavailableError,
    RateLimitExceededError,
    run_document_comparison,
)
from report_generator import build_docx_report, build_pdf_report

# Load environment configuration
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Document Comparison Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CSS Styling & Animations (Clean SaaS Palette: Navy, Electric Blue, Violet, Slate)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Import Inter Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0f172a;
}

/* Background refinement */
.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Header Container */
.hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
    border-radius: 16px;
    padding: 32px 36px;
    color: #ffffff;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
    margin-bottom: 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    margin: 0 0 8px 0;
    background: linear-gradient(135deg, #ffffff 60%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.05rem;
    font-weight: 400;
    color: #cbd5e1;
    margin: 0 0 16px 0;
    line-height: 1.5;
}

.hero-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.hero-pill {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #e2e8f0;
}

/* Document Upload Cards */
.upload-card-a {
    background: #ffffff;
    border: 1.5px solid #bfdbfe;
    border-top: 4px solid #2563eb;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.05);
    margin-bottom: 20px;
}

.upload-card-b {
    background: #ffffff;
    border: 1.5px solid #ddd6fe;
    border-top: 4px solid #7c3aed;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.05);
    margin-bottom: 20px;
}

.card-title-a {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e40af;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.card-title-b {
    font-size: 1.15rem;
    font-weight: 700;
    color: #5b21b6;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

/* Metadata Badge Container */
.meta-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    margin-top: 10px;
    font-size: 0.85rem;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
}

.meta-item {
    color: #475569;
}

.meta-item strong {
    color: #0f172a;
}

/* Diff Pill Tags */
.tag-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}

.tag-addition {
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.tag-removal {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.tag-modification {
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
}

.tag-contradiction {
    background-color: #fce7f3;
    color: #9d174d;
    border: 1px solid #fbcfe8;
}

.tag-scope {
    background-color: #e0e7ff;
    color: #3730a3;
    border: 1px solid #c7d2fe;
}

/* Card Styling for Results */
.result-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-card:hover {
    box-shadow: 0 6px 12px -2px rgba(15, 23, 42, 0.06);
    transform: translateY(-1px);
}

.quote-box {
    background: #f1f5f9;
    border-left: 3px solid #3b82f6;
    padding: 8px 14px;
    font-style: italic;
    color: #334155;
    font-size: 0.85rem;
    border-radius: 0 6px 6px 0;
    margin-top: 6px;
}

.page-chip {
    background: #e2e8f0;
    color: #334155;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 500;
}

/* Footer Container */
.app-footer {
    border-top: 1px solid #e2e8f0;
    margin-top: 40px;
    padding-top: 20px;
    padding-bottom: 20px;
    text-align: center;
    color: #64748b;
    font-size: 0.85rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Management
# -----------------------------------------------------------------------------
def initialize_session_state():
    """Initializes persistent application session variables."""
    if "doc_a" not in st.session_state:
        st.session_state.doc_a = None  # ExtractedDocument
    if "doc_b" not in st.session_state:
        st.session_state.doc_b = None  # ExtractedDocument
    if "comparison_result" not in st.session_state:
        st.session_state.comparison_result = None  # ComparisonResult
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "api_error" not in st.session_state:
        st.session_state.api_error = None
    if "sample_loaded" not in st.session_state:
        st.session_state.sample_loaded = False
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0


initialize_session_state()


def reset_comparison_state():
    """Completely resets document data and comparison results."""
    st.session_state.doc_a = None
    st.session_state.doc_b = None
    st.session_state.comparison_result = None
    st.session_state.is_processing = False
    st.session_state.api_error = None
    st.session_state.sample_loaded = False
    st.session_state.uploader_key += 1
    st.rerun()


# -----------------------------------------------------------------------------
# Sidebar Configuration & Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")

    # API Key Input / Override
    env_key = os.getenv("GEMINI_API_KEY", "")
    has_env_key = bool(env_key and env_key != "your_actual_api_key_here")

    if has_env_key:
        st.success("🟢 API Key Loaded (.env)")
        user_key_input = st.text_input(
            "API Key Override (Optional)",
            type="password",
            placeholder="Leave empty to use .env key",
            help="If provided, overrides the key from the .env file.",
        )
        active_api_key = user_key_input.strip() if user_key_input.strip() else env_key
    else:
        st.warning("⚠️ No GEMINI_API_KEY found in .env")
        user_key_input = st.text_input(
            "Enter Gemini API Key",
            type="password",
            placeholder="Paste your Gemini API key here",
            help="Your key will not be logged, saved to disk, or exposed.",
        )
        active_api_key = user_key_input.strip() if user_key_input.strip() else None

    # Model Selection
    env_model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    model_options = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    if env_model not in model_options:
        model_options.insert(0, env_model)

    active_model = st.selectbox(
        "Gemini Model",
        options=model_options,
        index=0,
        help="Select the active Google GenAI model. 'gemini-3.8-flash' is the currently supported standard.",
    )

    st.markdown("---")
    st.markdown("### 🧪 Quick Demo Sample")
    st.caption("Load pre-configured academic syllabus versions (v1 vs v2) with 1 click to test the entire comparison engine immediately.")

    if st.button("🚀 Load Sample Documents", use_container_width=True):
        sample_a_path = os.path.join(os.path.dirname(__file__), "sample_documents", "document_a.pdf")
        sample_b_path = os.path.join(os.path.dirname(__file__), "sample_documents", "document_b.pdf")

        if os.path.exists(sample_a_path) and os.path.exists(sample_b_path):
            with open(sample_a_path, "rb") as fa:
                st.session_state.doc_a = extract_text_from_pdf(fa.read(), "document_a.pdf")
            with open(sample_b_path, "rb") as fb:
                st.session_state.doc_b = extract_text_from_pdf(fb.read(), "document_b.pdf")
            st.session_state.sample_loaded = True
            st.session_state.comparison_result = None
            st.session_state.api_error = None
            st.rerun()
        else:
            st.error("Sample document files not found on disk.")

    st.markdown("---")
    # Quick Viva & Architecture helper
    with st.expander("📚 Internship Viva Quick Guide"):
        st.markdown("""
        **Key Architectural Highlights:**
        - **Separation of Concerns:** `document_reader.py` (extraction & safety), `comparison.py` (AI prompts & schemas), `report_generator.py` (ReportLab & DOCX), `app.py` (Streamlit).
        - **Strict Evidence Grounding:** AI system instructions prohibit external assumption; missing details return *"Not found in the provided text."*
        - **Page Citations:** Extracted text tags `[Page X]` markers preserved across API payloads.
        - **Dual Format Export:** Clean binary streaming for PDF (ReportLab) and DOCX (python-docx).
        """)

    st.markdown("---")
    max_mb, max_pg = get_configured_limits()
    st.caption(f"🛡️ Safety Limits: Max {max_mb} MB per file • Max {max_pg} pages per document")


# -----------------------------------------------------------------------------
# Main Hero Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">⚖️ AI Document Comparison Assistant</div>
        <div class="hero-subtitle">
            Upload two PDF documents (e.g. policies, specifications, syllabi, or agreements) to generate
            independent summaries, detect verifiable similarities, itemize granular differences, and download professional comparison reports.
        </div>
        <div class="hero-badges">
            <span class="hero-pill">📄 Independent Text Extraction</span>
            <span class="hero-pill">🔍 Strict Grounded Comparison</span>
            <span class="hero-pill">🏷️ Page-Level Source Traceability</span>
            <span class="hero-pill">📥 PDF & DOCX Export</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Document Upload Workspace (Document A and Document B)
# -----------------------------------------------------------------------------
col_a, col_b = st.columns(2)

# --- Document A ---
with col_a:
    st.markdown(
        """
        <div class="upload-card-a">
            <div class="card-title-a">📘 Document A (Baseline / Reference)</div>
        """,
        unsafe_allow_html=True,
    )

    uploader_a = st.file_uploader(
        "Upload Document A (PDF)",
        type=["pdf"],
        key=f"file_uploader_a_{st.session_state.uploader_key}",
        help="Upload the reference version (e.g. original syllabus or baseline contract).",
    )

    if uploader_a is not None:
        file_bytes_a = uploader_a.read()
        st.session_state.doc_a = extract_text_from_pdf(file_bytes_a, uploader_a.name)
        st.session_state.sample_loaded = False

    # Render Document A status
    doc_a = st.session_state.doc_a
    if doc_a:
        if doc_a.is_valid:
            st.success(f"✅ Ready: **{doc_a.filename}**")
            st.markdown(
                f"""
                <div class="meta-box">
                    <span class="meta-item">Size: <strong>{doc_a.file_size_display}</strong></span>
                    <span class="meta-item">Pages: <strong>{doc_a.page_count}</strong></span>
                    <span class="meta-item">Characters: <strong>{doc_a.char_count:,}</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("👁️ Preview Extracted Text (Doc A)"):
                st.caption(f"Displaying first 400 characters of {doc_a.char_count} total characters:")
                st.code(doc_a.preview_text or "No text", language="text")
        else:
            st.error(f"❌ {doc_a.validation_error}")
            if doc_a.is_scanned_or_empty:
                st.info("ℹ️ Scanned documents or vector-outlined text without font glyphs cannot be parsed without OCR.")
    else:
        st.info("Upload a PDF to establish Document A baseline.")

    st.markdown("</div>", unsafe_allow_html=True)


# --- Document B ---
with col_b:
    st.markdown(
        """
        <div class="upload-card-b">
            <div class="card-title-b">📗 Document B (Revised / Comparison)</div>
        """,
        unsafe_allow_html=True,
    )

    uploader_b = st.file_uploader(
        "Upload Document B (PDF)",
        type=["pdf"],
        key=f"file_uploader_b_{st.session_state.uploader_key}",
        help="Upload the modified version to compare against Document A.",
    )

    if uploader_b is not None:
        file_bytes_b = uploader_b.read()
        st.session_state.doc_b = extract_text_from_pdf(file_bytes_b, uploader_b.name)
        st.session_state.sample_loaded = False

    # Render Document B status
    doc_b = st.session_state.doc_b
    if doc_b:
        if doc_b.is_valid:
            st.success(f"✅ Ready: **{doc_b.filename}**")
            st.markdown(
                f"""
                <div class="meta-box">
                    <span class="meta-item">Size: <strong>{doc_b.file_size_display}</strong></span>
                    <span class="meta-item">Pages: <strong>{doc_b.page_count}</strong></span>
                    <span class="meta-item">Characters: <strong>{doc_b.char_count:,}</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("👁️ Preview Extracted Text (Doc B)"):
                st.caption(f"Displaying first 400 characters of {doc_b.char_count} total characters:")
                st.code(doc_b.preview_text or "No text", language="text")
        else:
            st.error(f"❌ {doc_b.validation_error}")
            if doc_b.is_scanned_or_empty:
                st.info("ℹ️ Scanned documents or vector-outlined text without font glyphs cannot be parsed without OCR.")
    else:
        st.info("Upload a PDF to establish Document B for comparison.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Comparison Action Bar
# -----------------------------------------------------------------------------
docs_ready = bool(
    st.session_state.doc_a
    and st.session_state.doc_b
    and st.session_state.doc_a.is_valid
    and st.session_state.doc_b.is_valid
)

action_col1, action_col2 = st.columns([3, 1])

with action_col1:
    compare_btn = st.button(
        "⚡ Compare Documents with Gemini AI",
        type="primary",
        disabled=not docs_ready or st.session_state.is_processing,
        use_container_width=True,
        help="Execute AI comparison on extracted text from Document A and Document B." if docs_ready else "Both Document A and Document B must be valid text-based PDFs before comparison.",
    )

with action_col2:
    if st.button("🔄 Start New Comparison", use_container_width=True, help="Clear all documents and comparison results."):
        reset_comparison_state()

# Helpful prompt if documents are missing
if not docs_ready and (st.session_state.doc_a or st.session_state.doc_b):
    st.warning("⚠️ Please ensure both Document A and Document B are uploaded and contain readable text.")


# -----------------------------------------------------------------------------
# Execution & Progress Workflow
# -----------------------------------------------------------------------------
if compare_btn and docs_ready:
    if not active_api_key:
        st.error("🔑 Missing Gemini API Key. Please configure GEMINI_API_KEY in `.env` or input it in the sidebar.")
    else:
        st.session_state.is_processing = True
        st.session_state.api_error = None

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.markdown("⏳ **Stage 1/4:** Validating extracted text streams and page indices...")
            progress_bar.progress(25)
            time.sleep(0.3)

            status_text.markdown(f"🤖 **Stage 2/4:** Dispatching structured payload to Gemini ({active_model})...")
            progress_bar.progress(50)

            # Build text representations with explicit [Page X] tags
            text_a = st.session_state.doc_a.get_text_with_page_labels()
            text_b = st.session_state.doc_b.get_text_with_page_labels()

            status_text.markdown("🧠 **Stage 3/4:** Analyzing cross-document differences, additions, and similarities...")
            progress_bar.progress(75)

            # Execute comparison
            result = run_document_comparison(
                doc_a_name=st.session_state.doc_a.filename,
                doc_a_text_with_pages=text_a,
                doc_b_name=st.session_state.doc_b.filename,
                doc_b_text_with_pages=text_b,
                api_key=active_api_key,
                model_name=active_model,
            )

            status_text.markdown("✅ **Stage 4/4:** Validating structured Pydantic schema and building reports...")
            progress_bar.progress(100)
            time.sleep(0.4)

            st.session_state.comparison_result = result
            st.session_state.is_processing = False
            progress_bar.empty()
            status_text.empty()
            st.rerun()

        except MissingApiKeyError as e:
            st.session_state.is_processing = False
            st.session_state.api_error = f"Missing API Key: {str(e)}"
            progress_bar.empty()
            status_text.empty()
        except InvalidApiKeyError as e:
            st.session_state.is_processing = False
            st.session_state.api_error = f"Authentication Error: {str(e)}"
            progress_bar.empty()
            status_text.empty()
        except ModelUnavailableError as e:
            st.session_state.is_processing = False
            st.session_state.api_error = f"Model Unavailable: {str(e)}"
            progress_bar.empty()
            status_text.empty()
        except RateLimitExceededError as e:
            st.session_state.is_processing = False
            st.session_state.api_error = f"Rate Limit Hit: {str(e)}"
            progress_bar.empty()
            status_text.empty()
        except MalformedResponseError as e:
            st.session_state.is_processing = False
            st.session_state.api_error = f"Malformed AI Response: {str(e)}"
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            st.session_state.is_processing = False
            st.session_state.api_error = f"Comparison Error: {str(e)}"
            progress_bar.empty()
            status_text.empty()


# Display API error with retry recommendation if triggered
if st.session_state.api_error:
    st.error(f"❌ {st.session_state.api_error}")
    st.info("💡 You can verify your API key or model name in the sidebar and retry comparison.")


# -----------------------------------------------------------------------------
# Results Dashboard & Report Export
# -----------------------------------------------------------------------------
res: Optional[ComparisonResult] = st.session_state.comparison_result

if res:
    st.markdown("---")
    st.markdown("## 📊 Comparison Dashboard & Findings")

    # 1. Executive Highlights Banner
    st.markdown(
        f"""
        <div class="result-card" style="border-left: 4px solid #2563eb; background: #ffffff;">
            <h4 style="margin: 0 0 8px 0; color: #1e3a8a;">📌 Executive Synthesis</h4>
            <p style="margin: 0; color: #334155; line-height: 1.6;">{res.overall_conclusion.neutral_summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Main Tabbed Navigation
    tab_diff, tab_profiles, tab_sim, tab_matrix, tab_conclusion = st.tabs([
        f"⚡ Differences ({len(res.differences)})",
        "📑 Document Profiles",
        f"🤝 Similarities ({len(res.similarities)})",
        f"📊 Key Details Matrix ({len(res.key_details)})",
        "🎯 Conclusion & Limitations",
    ])

    # -------------------------------------------------------------
    # TAB 1: Granular Differences
    # -------------------------------------------------------------
    with tab_diff:
        st.markdown("### Itemized Differences & Discrepancies")
        st.caption("All additions, removals, modified requirements, contradictions, and deliverable changes grounded in document text.")

        if res.differences:
            # Filter by Category
            categories = list(set(d.category for d in res.differences))
            selected_cat = st.multiselect(
                "Filter by category:",
                options=categories,
                default=categories,
            )

            filtered_diffs = [d for d in res.differences if d.category in selected_cat]

            for idx, diff in enumerate(filtered_diffs):
                cat_lower = diff.category.lower()
                badge_class = "tag-modification"
                if "addition" in cat_lower or "add" in cat_lower:
                    badge_class = "tag-addition"
                elif "removal" in cat_lower or "remov" in cat_lower:
                    badge_class = "tag-removal"
                elif "contradiction" in cat_lower:
                    badge_class = "tag-contradiction"
                elif "scope" in cat_lower or "deliverable" in cat_lower:
                    badge_class = "tag-scope"

                st.markdown(
                    f"""
                    <div class="result-card">
                        <span class="tag-badge {badge_class}">{diff.category}</span>
                        <h4 style="margin: 4px 0 8px 0; color: #0f172a;">{diff.topic}</h4>
                        <p style="margin: 0 0 10px 0; color: #334155;">{diff.description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Two-column comparison state
                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    st.markdown(f"**Doc A ({diff.doc_a_page}):** {diff.doc_a_state}")
                with dcol2:
                    st.markdown(f"**Doc B ({diff.doc_b_page}):** {diff.doc_b_state}")

                if diff.quote_excerpt and diff.quote_excerpt != "Not found in the provided text.":
                    st.markdown(
                        f"""<div class="quote-box">Quote Excerpt: "{diff.quote_excerpt}"</div>""",
                        unsafe_allow_html=True,
                    )
                st.markdown("<br/>", unsafe_allow_html=True)
        else:
            st.info("No significant differences were identified between Document A and Document B.")

    # -------------------------------------------------------------
    # TAB 2: Document Profiles (Summaries)
    # -------------------------------------------------------------
    with tab_profiles:
        st.markdown("### Independent Document Profiles")
        st.caption("Exhaustive, unmixed summaries extracted solely from each respective document.")

        pcol1, pcol2 = st.columns(2)

        with pcol1:
            st.markdown(f"#### 📘 {res.doc_a_summary.filename}")
            st.markdown(f"**Purpose:** {res.doc_a_summary.main_purpose}")
            st.markdown(f"**Summary:** {res.doc_a_summary.executive_summary}")

            if res.doc_a_summary.main_topics:
                st.markdown("**Main Topics:**")
                for topic in res.doc_a_summary.main_topics:
                    st.markdown(f"- {topic}")

            if res.doc_a_summary.important_requirements:
                st.markdown("**Requirements & Policies:**")
                for req in res.doc_a_summary.important_requirements:
                    st.markdown(f"- {req}")

            if res.doc_a_summary.dates_and_deadlines:
                st.markdown("**Dates & Deadlines:**")
                for date in res.doc_a_summary.dates_and_deadlines:
                    st.markdown(f"- 📅 {date}")

            if res.doc_a_summary.names_and_entities:
                st.markdown("**Entities & Roles:**")
                for ent in res.doc_a_summary.names_and_entities:
                    st.markdown(f"- 👤 {ent}")

        with pcol2:
            st.markdown(f"#### 📗 {res.doc_b_summary.filename}")
            st.markdown(f"**Purpose:** {res.doc_b_summary.main_purpose}")
            st.markdown(f"**Summary:** {res.doc_b_summary.executive_summary}")

            if res.doc_b_summary.main_topics:
                st.markdown("**Main Topics:**")
                for topic in res.doc_b_summary.main_topics:
                    st.markdown(f"- {topic}")

            if res.doc_b_summary.important_requirements:
                st.markdown("**Requirements & Policies:**")
                for req in res.doc_b_summary.important_requirements:
                    st.markdown(f"- {req}")

            if res.doc_b_summary.dates_and_deadlines:
                st.markdown("**Dates & Deadlines:**")
                for date in res.doc_b_summary.dates_and_deadlines:
                    st.markdown(f"- 📅 {date}")

            if res.doc_b_summary.names_and_entities:
                st.markdown("**Entities & Roles:**")
                for ent in res.doc_b_summary.names_and_entities:
                    st.markdown(f"- 👤 {ent}")

    # -------------------------------------------------------------
    # TAB 3: Similarities
    # -------------------------------------------------------------
    with tab_sim:
        st.markdown("### Common Ground & Unchanged Content")
        st.caption("Content, terms, and requirements that remain consistent across both versions.")

        if res.similarities:
            for sim in res.similarities:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <h4 style="margin: 0 0 6px 0; color: #0d9488;">✓ {sim.topic}</h4>
                        <p style="margin: 0 0 6px 0; color: #334155;">{sim.description}</p>
                        <div style="font-size: 0.8rem; color: #64748b;">
                            <span class="page-chip">Doc A: {sim.doc_a_page}</span> &nbsp;
                            <span class="page-chip">Doc B: {sim.doc_b_page}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if sim.quote_excerpt and sim.quote_excerpt != "Not found in the provided text.":
                    st.markdown(
                        f"""<div class="quote-box">Quote: "{sim.quote_excerpt}"</div>""",
                        unsafe_allow_html=True,
                    )
                st.markdown("<br/>", unsafe_allow_html=True)
        else:
            st.info("No matching similarities were identified.")

    # -------------------------------------------------------------
    # TAB 4: Key Details Matrix
    # -------------------------------------------------------------
    with tab_matrix:
        st.markdown("### Key Operational Details Comparison")
        st.caption("Side-by-side comparison across standard fields like Dates, Numbers, Eligibility, Deliverables, and Tech Stack.")

        if res.key_details:
            matrix_data = []
            for item in res.key_details:
                matrix_data.append({
                    "Operational Field": item.field_name,
                    "Document A": item.doc_a_value,
                    "Document B": item.doc_b_value,
                    "Status": item.status,
                    "Notes": item.notes,
                })
            st.dataframe(matrix_data, use_container_width=True, hide_index=True)
        else:
            st.info("No key operational details available.")

    # -------------------------------------------------------------
    # TAB 5: Conclusion & Limitations
    # -------------------------------------------------------------
    with tab_conclusion:
        st.markdown("### Overall Conclusion & Risk Areas")
        st.markdown(f"**Core Evolutionary Shifts:** {res.overall_conclusion.main_changes}")

        if res.overall_conclusion.most_significant_differences:
            st.markdown("#### 🌟 Top Impactful Differences:")
            for item in res.overall_conclusion.most_significant_differences:
                st.markdown(f"- {item}")

        if res.overall_conclusion.areas_requiring_attention:
            st.markdown("#### ⚠️ Areas Requiring Special Scrutiny:")
            for item in res.overall_conclusion.areas_requiring_attention:
                st.warning(item)

        st.markdown("---")
        st.markdown("### 🔍 Analysis Limitations & Governance")
        if res.limitations.unreadable_or_missing_content:
            st.markdown("**Unreadable / Missing Content:**")
            for unc in res.limitations.unreadable_or_missing_content:
                st.markdown(f"- {unc}")

        if res.limitations.processing_notes:
            st.markdown("**Processing & Scope Notes:**")
            for note in res.limitations.processing_notes:
                st.caption(f"• {note}")

    # -------------------------------------------------------------
    # Report Export Actions
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📥 Download Formal Comparison Report")
    st.caption("Export this complete analysis package into formatted, ready-to-share documents.")

    exp_col1, exp_col2, _ = st.columns([1, 1, 2])

    with exp_col1:
        # Generate ReportLab PDF in memory
        try:
            pdf_bytes = build_pdf_report(res)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"Document_Comparison_Report_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error compiling PDF: {str(e)}")

    with exp_col2:
        # Generate DOCX in memory
        try:
            docx_bytes = build_docx_report(res)
            st.download_button(
                label="📝 Download Word (.docx) Report",
                data=docx_bytes,
                file_name=f"Document_Comparison_Report_{int(time.time())}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error compiling DOCX: {str(e)}")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        <strong>AI Document Comparison Assistant</strong> &nbsp;|&nbsp;
        AI Engineering Internship Project &nbsp;|&nbsp;
        <em>Informational use only. Does not constitute legal, compliance, or professional advice.</em>
    </div>
    """,
    unsafe_allow_html=True,
)
