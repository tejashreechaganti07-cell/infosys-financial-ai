from crewai import Agent
from crewai.tools import tool

from pypdf import PdfReader
import pymupdf
import pdfplumber

import json
import re
import os


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def read_pdf(file_path):
    """
    Extract text from every page.

    Primary parser:
        pypdf

    Fallback parser:
        PyMuPDF

    If a page cannot be read by pypdf, PyMuPDF is used
    for that page instead of stopping the whole document.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    pages = []

    # --------------------------------------------------------
    # First attempt: pypdf
    # --------------------------------------------------------

    reader = None

    try:
        reader = PdfReader(
            file_path,
            strict=False
        )

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:
                text = page.extract_text() or ""

            except Exception as e:
                print(
                    f"Warning: pypdf failed on page "
                    f"{page_number}: {e}"
                )

                text = ""

            pages.append(
                {
                    "page_number": page_number,
                    "text": text
                }
            )

    except Exception as e:

        print(
            f"Warning: pypdf could not open the PDF: {e}"
        )

    # --------------------------------------------------------
    # Second attempt: PyMuPDF fallback
    # --------------------------------------------------------

    try:

        pdf = pymupdf.open(file_path)

        for page_index in range(len(pdf)):

            page_number = page_index + 1

            # Create missing page entry
            if page_number > len(pages):

                pages.append(
                    {
                        "page_number": page_number,
                        "text": ""
                    }
                )

            # Only use fallback if pypdf produced no text
            if not pages[page_index]["text"].strip():

                try:

                    fallback_text = (
                        pdf[page_index]
                        .get_text("text")
                    )

                    if fallback_text.strip():

                        pages[page_index]["text"] = (
                            fallback_text
                        )

                except Exception as e:

                    print(
                        f"Warning: PyMuPDF failed on "
                        f"page {page_number}: {e}"
                    )

        pdf.close()

    except Exception as e:

        print(
            f"Warning: PyMuPDF could not open PDF: {e}"
        )

    return pages


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(
    text,
    chunk_size=4000,
    overlap=400
):
    """
    Split text into overlapping chunks.

    Default:
        chunk size = 4000 characters
        overlap = 400 characters
    """

    chunks = []

    if not text:
        return chunks

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# ============================================================
# SECTION DETECTION
# ============================================================

KNOWN_HEADINGS = {
    "business",
    "risk factors",
    "unresolved staff comments",
    "cybersecurity",
    "properties",
    "legal proceedings",
    "mine safety disclosures",

    "market for registrant's common equity, "
    "related stockholder matters and issuer "
    "purchases of equity securities",

    "market for registrant’s common equity, "
    "related stockholder matters and issuer "
    "purchases of equity securities",

    "management's discussion and analysis of "
    "financial condition and results of operations",

    "management’s discussion and analysis of "
    "financial condition and results of operations",

    "quantitative and qualitative disclosures "
    "about market risk",

    "financial statements and supplementary data",

    "changes in and disagreements with accountants "
    "on accounting and financial disclosure",

    "controls and procedures",

    "other information",

    "directors, executive officers and "
    "corporate governance",

    "executive compensation",

    "security ownership of certain beneficial "
    "owners and management and related "
    "stockholder matters",

    "certain relationships and related transactions, "
    "and director independence",

    "principal accountant fees and services",

    "exhibit and financial statement schedules",

    "form 10-k summary",

    "[reserved]",
}


def clean_heading(line):
    """
    Clean section heading text.

    Removes:
        Item 1.
        Item 1A.
        trailing page numbers
    """

    cleaned = line.strip()

    # Remove SEC numbering
    cleaned = re.sub(
        r"^item\s+\d+[a-z]?\s*[\.\:\-\)]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove trailing page number
    cleaned = re.sub(
        r"\s+\d{1,3}$",
        "",
        cleaned
    )

    return cleaned.strip()


def is_section_heading(line):
    """
    Determine whether a line is a meaningful section heading.

    Conservative detection is intentional so that normal
    financial text and table-of-content entries are not
    incorrectly treated as sections.
    """

    if not line:
        return False

    cleaned = clean_heading(line)

    normalized = cleaned.lower().strip()

    # --------------------------------------------------------
    # Do not treat TOC-style lines as headings
    # --------------------------------------------------------

    # Example:
    # Mine Safety Disclosures 18
    if re.search(r"\s+\d{1,3}$", line.strip()):
        return False

    # --------------------------------------------------------
    # Exact known financial headings
    # --------------------------------------------------------

    if normalized in KNOWN_HEADINGS:
        return True

    # --------------------------------------------------------
    # SEC Item headings
    #
    # Example:
    # Item 1. Business
    # Item 1A. Risk Factors
    # --------------------------------------------------------

    if re.match(
        r"^item\s+\d+[a-z]?\s+.+",
        line.strip(),
        re.IGNORECASE
    ):
        return True

    return False


# ============================================================
# DOCUMENT SECTION PROCESSING
# ============================================================

def build_sections(pages):
    """
    Process pages sequentially while maintaining the current
    section across page boundaries.

    This prevents every new page from starting again under
    'General'.
    """

    sections = {}

    current_section = "General"

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        if not text.strip():
            continue

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        current_lines = []

        for line in lines:

            # ------------------------------------------------
            # New section detected
            # ------------------------------------------------

            if is_section_heading(line):

                # Save previous content before changing section
                if current_lines:

                    section_text = "\n".join(
                        current_lines
                    ).strip()

                    if section_text:

                        if current_section not in sections:

                            sections[current_section] = {
                                "pages": [],
                                "chunks": []
                            }

                        if page_number not in sections[
                            current_section
                        ]["pages"]:

                            sections[
                                current_section
                            ]["pages"].append(
                                page_number
                            )

                        sections[
                            current_section
                        ]["chunks"].extend(
                            chunk_text(section_text)
                        )

                    current_lines = []

                # Update current section
                current_section = clean_heading(line)

            else:

                current_lines.append(line)

        # ----------------------------------------------------
        # Save remaining text on this page
        # ----------------------------------------------------

        if current_lines:

            section_text = "\n".join(
                current_lines
            ).strip()

            if section_text:

                if current_section not in sections:

                    sections[current_section] = {
                        "pages": [],
                        "chunks": []
                    }

                if page_number not in sections[
                    current_section
                ]["pages"]:

                    sections[
                        current_section
                    ]["pages"].append(
                        page_number
                    )

                sections[
                    current_section
                ]["chunks"].extend(
                    chunk_text(section_text)
                )

    return sections


# ============================================================
# TABLE EXTRACTION
# ============================================================

def extract_tables(file_path):
    """
    Extract tables from PDF pages using pdfplumber.

    Returns structured table information.
    """

    tables = []

    try:

        with pdfplumber.open(file_path) as pdf:

            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                try:

                    page_tables = page.extract_tables()

                    for table_number, table in enumerate(
                        page_tables,
                        start=1
                    ):

                        if not table:
                            continue

                        cleaned_rows = []

                        for row in table:

                            if not row:
                                continue

                            cleaned_row = [
                                (
                                    str(cell).strip()
                                    if cell is not None
                                    else ""
                                )
                                for cell in row
                            ]

                            cleaned_rows.append(
                                cleaned_row
                            )

                        if cleaned_rows:

                            tables.append(
                                {
                                    "page_number": page_number,
                                    "table_number": table_number,
                                    "rows": cleaned_rows
                                }
                            )

                except Exception as e:

                    print(
                        f"Warning: table extraction "
                        f"failed on page {page_number}: {e}"
                    )

    except Exception as e:

        print(
            f"Warning: pdfplumber could not open PDF: {e}"
        )

    return tables


# ============================================================
# MAIN CREWAI TOOL
# ============================================================

@tool
def process_pdf(file_path):
    """
    Process a financial PDF.

    Performs:

    1. PDF validation
    2. Text extraction
    3. Fallback extraction
    4. Section detection
    5. Chunking
    6. Table extraction
    7. Structured JSON generation
    """

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not file_path:
        raise ValueError(
            "A PDF file path is required."
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    if not file_path.lower().endswith(".pdf"):
        raise ValueError(
            "Only PDF files are supported."
        )

    # --------------------------------------------------------
    # Extract pages
    # --------------------------------------------------------

    pages = read_pdf(file_path)

    if not pages:
        raise ValueError(
            "No pages could be extracted from the PDF."
        )

    # --------------------------------------------------------
    # Build sections
    # --------------------------------------------------------

    sections = build_sections(pages)

    # --------------------------------------------------------
    # Extract tables
    # --------------------------------------------------------

    tables = extract_tables(file_path)

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    total_chunks = sum(
        len(section["chunks"])
        for section in sections.values()
    )

    result = {

        "filename": os.path.basename(file_path),

        "file_type": "application/pdf",

        "page_count": len(pages),

        "section_count": len(sections),

        "chunk_count": total_chunks,

        "table_count": len(tables),

        "sections": sections,

        "tables": tables
    }

    return json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# CREWAI AGENT
# ============================================================

document_agent = Agent(

    role="Financial Document Processing Specialist",

    goal=(
        "Process uploaded financial documents and prepare "
        "clean structured information for downstream "
        "financial analysis agents."
    ),

    backstory=(
        "You are responsible for processing financial "
        "documents. You validate PDF files, extract text, "
        "detect meaningful financial sections, create "
        "overlapping chunks, extract tables, and prepare "
        "structured JSON for downstream financial analysis."
    ),

    tools=[process_pdf],

    verbose=True,

    allow_delegation=False
)


# ============================================================
# CREWAI TASK
# ============================================================

from crewai import Task


document_task = Task(

    description=(
        "Process the uploaded financial document using "
        "the document processing tool. Validate the PDF, "
        "extract its text, detect meaningful sections, "
        "create chunks, extract tables, and return the "
        "processed document as structured JSON."
    ),

    expected_output=(
        "A valid JSON-formatted representation of the "
        "financial document containing filename, page "
        "count, section count, chunk count, table count, "
        "section-wise page numbers and chunks, and "
        "extracted tables."
    ),

    agent=document_agent
)


# ============================================================
# CREW
# ============================================================

from crewai import Crew


document_crew = Crew(

    agents=[document_agent],

    tasks=[document_task],

    verbose=True
)