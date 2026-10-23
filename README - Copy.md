# AI Document Comparison Assistant ⚖️

> **Xpert Champs AI Engineering Internship — Project Assignment 1**  
> An intelligent, evidence-grounded web application that ingests, validates, summarizes, and deeply compares two PDF documents using **Google Gemini AI**, **Streamlit**, **pypdf**, and **ReportLab**.

---

## 🌟 Table of Contents
1. [Project Overview & Key Features](#-project-overview--key-features)
2. [Technical Architecture & Folder Structure](#-technical-architecture--folder-structure)
3. [Prerequisites & Environment Setup](#-prerequisites--environment-setup)
4. [Windows PowerShell Setup Commands](#-windows-powershell-setup-commands)
5. [Gemini API Key Configuration](#-gemini-api-key-configuration)
6. [Running the Application](#-running-the-application)
7. [Running the Automated Test Suite](#-running-the-automated-test-suite)
8. [Sample Demonstration Documents](#-sample-demonstration-documents)
9. [Report Generation (PDF & Word DOCX)](#-report-generation-pdf--word-docx)
10. [Troubleshooting Guide & Common Errors](#-troubleshooting-guide--common-errors)
11. [Current System Limitations & Scope Notice](#-current-system-limitations--scope-notice)
12. [Safe Git & GitHub Submission Guide](#-safe-git--github-submission-guide)
13. [Internship Viva Preparation & Technical Defense](#-internship-viva-preparation--technical-defense)

---

## 🚀 Project Overview & Key Features

The **AI Document Comparison Assistant** solves the real-world challenge of manual line-by-line document review across contract versions, course syllabi, policy manuals, and technical specifications. Rather than sending raw, unvalidated text to a generic chatbot, this application implements a strict engineering pipeline:

- **Independent PDF Ingestion & Validation:** Ensures both files are authentic text-based PDFs, enforcing strict safety limits (25 MB max file size, 50 pages maximum). Rejects 0-byte, corrupt, or password-protected files.
- **Scanned Document & OCR Safeguards:** Detects image-only, scanned, or vector-outlined PDFs and informs the user that OCR is not implemented, preventing empty tokens from wasting API quota.
- **Traceable Page Citations:** Injects `[Page X]` boundaries during extraction so findings, differences, and supporting quotes are traceable back to their exact source page.
- **Evidence-Grounded AI Comparison:** Operates under strict system instructions: document contents are treated as untrusted data, hallucinations are barred, and absent information is explicitly flagged as *"Not found in the provided text."*
- **Categorized Discrepancy Matrix:** Categorizes every identified change into **Additions in Doc B**, **Removals from Doc A**, **Modified Requirements**, **Contradictions**, **Scope Shifts**, and **Deliverable Changes**.
- **Side-by-Side Operational Matrix:** Formats operational fields (Dates/Deadlines, Entities/Roles, Numbers/Amounts, Eligibility Criteria, Required Technologies, Deliverables, Conditions) into an interactive table.
- **Multi-Format Formal Reports:** Compiles findings into downloadable **PDF reports** (with running headers/footers and dynamic page numbering via ReportLab) and editable **Microsoft Word (.docx)** documents.
- **Polished SaaS Interface:** Designed in Streamlit with an executive dark-navy and vivid blue/violet aesthetic, glassmorphic cards, responsive status badges, and 1-click sample loading.

---

## 🏛️ Technical Architecture & Folder Structure

```
ai-document-comparison-assistant/
│
├── app.py                     # Streamlit frontend, interactive dashboard, session state & UX
├── document_reader.py         # PDF validation, text extraction, page tracking & scanned detection
├── comparison.py              # Google GenAI SDK integration, system prompts, Pydantic schemas
├── report_generator.py        # Professional ReportLab PDF & python-docx Word export engine
├── requirements.txt           # Production dependency specifications
├── .env                       # Local private environment variables (DO NOT COMMIT)
├── .env.example               # Safe repository template for environment setup
├── .gitignore                 # Excludes .env, virtual environments, cache & temporary files
├── README.md                  # Comprehensive technical documentation & viva guide
│
├── sample_documents/          # Ready-to-use sample PDFs for demonstration & testing
│   ├── document_a.pdf         # AI Engineering Course Syllabus (Version 1.0 - 2025)
│   └── document_b.pdf         # AI Engineering Course Syllabus (Version 2.0 - Revised 2026)
│
└── tests/                     # Automated test suite (25 comprehensive pytest cases)
    ├── __init__.py
    ├── test_document_reader.py    # Tests for valid/empty/corrupt/scanned PDFs and limits
    ├── test_comparison.py         # Tests for prompt schemas, mock responses, API errors, long docs
    ├── test_report_generator.py   # Tests for ReportLab PDF & DOCX generation validity
    └── test_end_to_end.py         # Complete integration pipeline test
```

### Module Responsibilities:
1. `document_reader.py`: Encapsulates `pypdf.PdfReader` logic, validates file extensions and magic bytes (`%PDF-`), verifies encryption status, extracts page-by-page text into `PageData` objects, calculates character counts, and flags scanned/empty documents.
2. `comparison.py`: Leverages `google-genai` (v2.16+) using the official `genai.Client`. Enforces Pydantic models (`DocumentSummary`, `SimilarityItem`, `DifferenceItem`, `KeyDetailComparison`, `OverallConclusion`, `Limitations`, `ComparisonResult`). Implements retry backoff and error mapping.
3. `report_generator.py`: Custom ReportLab flowables, two-pass `NumberedCanvas` for *"Page X of Y"* pagination, styled comparison tables, and DOCX document builder.
4. `app.py`: Streamlit reactive UI, dual upload cards with live metadata preview, progress feedback, 5-tab results dashboard, and state reset.

---

## 📋 Prerequisites & Environment Setup

- **Operating System:** Windows 10 / 11, macOS, or Linux (Windows PowerShell commands documented below)
- **Python Version:** Python 3.10 to 3.14 (Tested on Python 3.14.6)
- **Google Gemini API Key:** Free API key obtainable from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## 💻 Windows PowerShell Setup Commands

Follow these exact commands in your Windows PowerShell terminal:

### Step 1: Open project directory
```powershell
cd d:\Xpertchamps_Internship_Pro_1
```

### Step 2: Create a virtual environment
```powershell
python -m venv venv
```

### Step 3: Activate the virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an `Execution_Policies` restriction, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

### Step 4: Upgrade pip & install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Gemini API Key Configuration

1. Copy `.env.example` to create your local `.env` file:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in any text editor (Notepad, VS Code) and set your actual Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   MAX_FILE_SIZE_MB=25
   MAX_PAGE_COUNT=50
   ```
   > 🔒 **Security Notice:** The `.env` file is explicitly ignored in `.gitignore`. **Never commit `.env` or your raw API key to GitHub.**

---

## 🚀 Running the Application

To launch the web interface, execute:
```powershell
python -m streamlit run app.py
```

Streamlit will initialize the server and open your default web browser at:
```
http://localhost:8501
```

### Testing with 1 Click:
In the left sidebar, click **"🚀 Load Sample Documents"**. The application will instantly load `document_a.pdf` (Syllabus v1) and `document_b.pdf` (Syllabus v2) into the upload cards. Click **"⚡ Compare Documents with Gemini AI"** to see live multi-stage analysis!

---

## 🧪 Running the Automated Test Suite

The project includes **25 automated pytest tests** covering extraction, validation, edge cases, schema parsing, mock API failures, long-document truncation, and report generation:

Run all tests:
```powershell
python -m pytest -v
```

### Test Coverage Highlights:
- ✅ `test_valid_text_pdf_extraction`: Validates extraction of multi-page text PDFs.
- ✅ `test_missing_filename` & `test_wrong_file_extension`: Rejects non-PDFs (`.docx`, `.txt`).
- ✅ `test_empty_zero_byte_pdf`: Rejects 0-byte uploaded files.
- ✅ `test_corrupt_pdf_content` & `test_missing_pdf_magic_header`: Catches invalid PDF headers.
- ✅ `test_scanned_or_image_only_pdf_behavior`: Detects image-only scans and notifies user about OCR.
- ✅ `test_file_size_limit_enforcement` & `test_page_count_limit_enforcement`: Enforces safety bounds.
- ✅ `test_missing_api_key_raises_error`: Validates friendly exception on absent API key.
- ✅ `test_clean_and_parse_json_*`: Tests markdown-fence stripping and conversational preamble cleanup.
- ✅ `test_run_document_comparison_successful_mock`: End-to-end mocked comparison validation.
- ✅ `test_long_document_safe_truncation`: Verifies token limit preservation on long files.
- ✅ `test_documents_with_different_dates_or_numbers`: Verifies accurate extraction of differing dates/metrics.
- ✅ `test_nearly_identical_documents_without_invented_differences`: Ensures zero invented differences.
- ✅ `test_pdf_report_generation_validity`: Validates ReportLab PDF binary structure and pagination.
- ✅ `test_docx_report_generation_validity`: Validates Word (.docx) export generation.
- ✅ `test_full_pipeline_with_sample_documents`: Full integration pipeline test.

---

## 📄 Sample Demonstration Documents

The repository includes pre-built sample files located in `sample_documents/`:
- **`document_a.pdf`**: AI Engineering Course Syllabus (Version 1.0 - Academic Year 2025)
  - 3.0 Credits, 12 Weeks (Sept 1 – Nov 24, 2025), Dr. Alan Vance
  - 6 Classical ML/DL modules, 3 Assignments, passing grade 70%, 10% daily late penalty.
- **`document_b.pdf`**: AI Engineering Course Syllabus (Version 2.0 - Academic Year 2026)
  - 4.0 Credits, 14 Weeks (Sept 15 – Dec 20, 2026), Dr. Alan Vance & Dr. Maya Lin
  - 8 modules (added Generative AI, Gemini API, RAG with ChromaDB, Streamlit)
  - 4 Assignments, Viva presentation (10%), passing grade 75%, 15% daily late penalty.

---

## 📊 Report Generation (PDF & Word DOCX)

Users can export the validated comparison result into two standalone formats directly from the UI:
1. **ReportLab PDF Report**:
   - Executive header and generation timestamp
   - Two-pass `NumberedCanvas` with running headers and *"Page X of Y"* footer
   - Side-by-side metadata and summaries
   - Formatted differences table with page-number citations and quote excerpts
   - Key details comparison matrix
   - Neutral conclusions and governance caveats
2. **Microsoft Word (.docx) Report**:
   - Formatted tables, headings, and bullet points ready for corporate editing.

---

## 🛠️ Troubleshooting Guide & Common Errors

| Issue / Error | Cause | Recommended Solution |
| :--- | :--- | :--- |
| `MissingApiKeyError: Gemini API key is not configured` | No `GEMINI_API_KEY` present in `.env` | Ensure `.env` exists in the project root with `GEMINI_API_KEY=your_key` or enter it directly in the sidebar. |
| `google.genai.errors.ClientError: 404 NOT_FOUND` | Specified model is deprecated or unavailable | Use `gemini-3.8-flash` in `.env` (`GEMINI_MODEL=gemini-3.8-flash`). |
| `google.genai.errors.ServerError: 503 UNAVAILABLE` | Temporary high demand on Google's free tier | The application automatically retries up to 3 times with exponential backoff. Simply click Compare again if spikes persist. |
| `No extractable text was found in '...'` | Uploaded PDF is scanned / rasterized image | The PDF lacks text font streams. Please use a text-based PDF or export from Word/Docs. |
| `File '...' exceeds maximum limit of 25 MB` | Uploaded PDF exceeds size limit | Compress the PDF or increase `MAX_FILE_SIZE_MB` in `.env`. |
| `The term 'pytest' is not recognized` | Virtual environment Scripts folder not in PATH | Run `python -m pytest -v` using the Python interpreter directly. |

---

## ⚠️ Current System Limitations & Scope Notice

1. **Optical Character Recognition (OCR):** The current version uses native font glyph extraction via `pypdf`. Hand-scanned physical documents and image-only PDFs without an embedded text layer require an OCR engine (such as Tesseract or Google Cloud Vision), which is intentionally excluded to keep dependencies lightweight.
2. **Context Window Safety:** For exceptionally large documents (> 50,000 characters), the system applies safe context truncation with an explicit audit note in the Limitations section to prevent token exhaustion.
3. **Informational Scope Disclaimer:** This software is an informational comparison assistant. It does not provide legal advice, regulatory compliance certification, or binding contract interpretation.

---

## 🐙 Safe Git & GitHub Submission Guide

To push your project to GitHub safely without leaking credentials:

### 1. Confirm `.env` is ignored
```powershell
git status
```
Verify that `.env` is **NOT** listed under untracked files. Only `.env.example` should be tracked.

### 2. Stage and commit files
```powershell
git add .
git commit -m "feat: complete AI Document Comparison Assistant project with tests and sample docs"
```

### 3. Link remote repository and push
```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-document-comparison-assistant.git
git push -u origin main
```

---

## 🎓 Internship Viva Preparation & Technical Defense

Here is how to answer common viva examination questions:

### Q1: Why did you separate text extraction from the LLM prompt?
> **Answer:** *"Sending raw PDF binary or uncontrolled text directly to an LLM risks token waste, prompt injection, and poor traceability. In `document_reader.py`, we validate magic bytes, check encryption, and inject `[Page X]` tags. This ensures that when Gemini detects a difference, it cites the exact source page number for human verification."*

### Q2: How do you prevent AI hallucinations when comparing documents?
> **Answer:** *"We use three strict defense layers: First, explicit system instructions treat document text as untrusted data and forbid external assumptions. Second, absent fields must return 'Not found in the provided text' rather than false deductions. Third, our output is strictly validated against a Pydantic schema (`ComparisonResult`) before reaching the UI or report generator."*

### Q3: How does the application handle corrupted or scanned PDFs?
> **Answer:** *"Before sending data to Gemini, `document_reader.py` verifies PDF magic bytes (`%PDF-`) and checks total extracted character count against `MIN_READABLE_CHARS_THRESHOLD`. If the character count is negligible, it flags the document as scanned/image-only and presents a clear message that OCR is not implemented, avoiding misleading empty comparisons."*

### Q4: Why use ReportLab and python-docx instead of browser printing?
> **Answer:** *"Browser printing is inconsistent across devices and browsers. `report_generator.py` uses ReportLab's programmatic flowables and a two-pass `NumberedCanvas` to draw running headers, crisp tables, and dynamic 'Page X of Y' pagination, producing formal, publication-ready PDF reports."*

---

### Project Credits & Authorship
- **Project Name:** AI Document Comparison Assistant
- **Internship:** Xpert Champs AI Engineering Internship
- **Primary Frameworks:** Python • Streamlit • Google GenAI • pypdf • ReportLab • python-docx • pytest
