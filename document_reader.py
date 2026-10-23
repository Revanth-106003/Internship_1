"""
document_reader.py
------------------
Module responsible for PDF validation, safe file ingestion, independent
text extraction using pypdf, per-page tracking, metadata calculation,
and empty/scanned document detection.
"""

import io
import os
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pypdf
from pypdf.errors import PdfReadError

# Default safety limits (can be overridden via environment variables)
DEFAULT_MAX_FILE_SIZE_MB = 25
DEFAULT_MAX_PAGE_COUNT = 50
MIN_READABLE_CHARS_THRESHOLD = 30  # Minimum characters across document to consider readable


@dataclass
class PageData:
    """Represents text extracted from a single PDF page."""
    page_num: int
    text: str
    char_count: int


@dataclass
class ExtractedDocument:
    """Encapsulates all extracted data, metadata, and validation status for a document."""
    filename: str
    file_size_bytes: int
    page_count: int = 0
    char_count: int = 0
    pages: List[PageData] = field(default_factory=list)
    full_text: str = ""
    preview_text: str = ""
    is_valid: bool = False
    validation_error: Optional[str] = None
    is_scanned_or_empty: bool = False

    @property
    def file_size_display(self) -> str:
        """Human-readable string of file size."""
        if self.file_size_bytes < 1024:
            return f"{self.file_size_bytes} B"
        elif self.file_size_bytes < 1024 * 1024:
            return f"{self.file_size_bytes / 1024:.1f} KB"
        else:
            return f"{self.file_size_bytes / (1024 * 1024):.2f} MB"

    def get_text_with_page_labels(self, max_chars: Optional[int] = None) -> str:
        """
        Formats document text with explicit [Page X] tags so LLM citations can be verified.
        Optionally truncates at max_chars safely.
        """
        formatted_sections = []
        accumulated_len = 0
        for page in self.pages:
            header = f"\n--- [Page {page.page_num}] ---\n"
            text_to_add = page.text.strip()
            if not text_to_add:
                continue
            section = f"{header}{text_to_add}"
            if max_chars and (accumulated_len + len(section) > max_chars):
                remaining = max_chars - accumulated_len
                if remaining > len(header) + 20:
                    formatted_sections.append(f"{header}{text_to_add[:remaining - len(header)]}... [truncated]")
                break
            formatted_sections.append(section)
            accumulated_len += len(section)
        return "\n".join(formatted_sections).strip()


def get_configured_limits() -> Tuple[int, int]:
    """Retrieves file size and page count limits from environment or defaults."""
    try:
        max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", DEFAULT_MAX_FILE_SIZE_MB))
    except (ValueError, TypeError):
        max_size_mb = DEFAULT_MAX_FILE_SIZE_MB

    try:
        max_pages = int(os.getenv("MAX_PAGE_COUNT", DEFAULT_MAX_PAGE_COUNT))
    except (ValueError, TypeError):
        max_pages = DEFAULT_MAX_PAGE_COUNT

    return max_size_mb, max_pages


def validate_pdf_file(
    file_bytes: bytes,
    filename: str,
    max_size_mb: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validates file extension, non-zero size, and PDF magic bytes.
    Returns (is_valid, error_message).
    """
    if max_size_mb is None:
        max_size_mb, _ = get_configured_limits()

    if not filename:
        return False, "No filename provided."

    if not filename.lower().endswith(".pdf"):
        return False, f"Invalid file extension for '{filename}'. Only .pdf files are supported."

    if not file_bytes or len(file_bytes) == 0:
        return False, f"The file '{filename}' is empty (0 bytes). Please upload a valid PDF."

    max_bytes = max_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return False, f"File '{filename}' ({len(file_bytes) / (1024 * 1024):.1f} MB) exceeds maximum limit of {max_size_mb} MB."

    # Validate PDF magic header bytes
    if not file_bytes.startswith(b"%PDF-"):
        return False, f"'{filename}' does not have a valid PDF header (%PDF-). It may be corrupted or not a real PDF."

    return True, None


def extract_text_from_pdf(
    file_bytes: bytes,
    filename: str,
    max_pages: Optional[int] = None
) -> ExtractedDocument:
    """
    Parses a PDF from raw bytes using pypdf, extracts text per page,
    preserves page indices, calculates metrics, and detects scanned/empty documents.
    """
    max_size_mb, env_max_pages = get_configured_limits()
    if max_pages is None:
        max_pages = env_max_pages

    is_valid, validation_err = validate_pdf_file(file_bytes, filename, max_size_mb)
    if not is_valid:
        return ExtractedDocument(
            filename=filename,
            file_size_bytes=len(file_bytes) if file_bytes else 0,
            is_valid=False,
            validation_error=validation_err
        )

    try:
        stream = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(stream)

        # Handle password protection / encryption
        if reader.is_encrypted:
            try:
                # Attempt to decrypt with empty password (some PDFs are encrypted with empty user password)
                decrypt_success = reader.decrypt("")
                if decrypt_success == 0:
                    return ExtractedDocument(
                        filename=filename,
                        file_size_bytes=len(file_bytes),
                        is_valid=False,
                        validation_error=f"'{filename}' is password-protected or encrypted. Please remove password protection before comparing."
                    )
            except Exception:
                return ExtractedDocument(
                    filename=filename,
                    file_size_bytes=len(file_bytes),
                    is_valid=False,
                    validation_error=f"'{filename}' is password-protected or encrypted. Please remove password protection before comparing."
                )

        total_pages = len(reader.pages)
        if total_pages == 0:
            return ExtractedDocument(
                filename=filename,
                file_size_bytes=len(file_bytes),
                page_count=0,
                is_valid=False,
                validation_error=f"'{filename}' has 0 pages."
            )

        if total_pages > max_pages:
            return ExtractedDocument(
                filename=filename,
                file_size_bytes=len(file_bytes),
                page_count=total_pages,
                is_valid=False,
                validation_error=f"'{filename}' has {total_pages} pages, which exceeds the limit of {max_pages} pages."
            )

        pages_data: List[PageData] = []
        extracted_text_parts: List[str] = []

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            try:
                page_text = page.extract_text() or ""
            except Exception as e:
                # In case a specific page fails to extract
                page_text = f"[Page extraction note: Could not parse page {page_num}: {str(e)}]"

            # Clean null bytes or rogue non-printable control characters
            clean_text = page_text.replace("\x00", "").strip()
            pages_data.append(PageData(page_num=page_num, text=clean_text, char_count=len(clean_text)))
            if clean_text:
                extracted_text_parts.append(clean_text)

        full_text = "\n\n".join(extracted_text_parts).strip()
        total_chars = len(full_text)

        # Detect scanned, image-only, or vector-outline PDF
        if total_chars < MIN_READABLE_CHARS_THRESHOLD:
            return ExtractedDocument(
                filename=filename,
                file_size_bytes=len(file_bytes),
                page_count=total_pages,
                char_count=total_chars,
                pages=pages_data,
                full_text=full_text,
                preview_text=full_text[:300],
                is_valid=False,
                is_scanned_or_empty=True,
                validation_error=(
                    f"No extractable text was found in '{filename}' ({total_pages} page(s), {total_chars} characters). "
                    "This usually means the PDF is an image-only scan or contains outlined vector graphics. "
                    "OCR (Optical Character Recognition) is not implemented in this version; please upload a text-based PDF."
                )
            )

        # Generate a clean short preview
        preview_text = full_text[:400] + ("..." if len(full_text) > 400 else "")

        return ExtractedDocument(
            filename=filename,
            file_size_bytes=len(file_bytes),
            page_count=total_pages,
            char_count=total_chars,
            pages=pages_data,
            full_text=full_text,
            preview_text=preview_text,
            is_valid=True,
            validation_error=None,
            is_scanned_or_empty=False
        )

    except PdfReadError as e:
        return ExtractedDocument(
            filename=filename,
            file_size_bytes=len(file_bytes),
            is_valid=False,
            validation_error=f"Corrupt or unreadable PDF file: {str(e)}"
        )
    except Exception as e:
        return ExtractedDocument(
            filename=filename,
            file_size_bytes=len(file_bytes),
            is_valid=False,
            validation_error=f"Failed to process '{filename}': {str(e)}"
        )
