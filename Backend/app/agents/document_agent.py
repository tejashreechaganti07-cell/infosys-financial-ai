from crewai import Agent
from crewai.tools import tool
from pypdf import PdfReader
import json
import re


def read_pdf(file_path):
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

    return pages


def chunk_text(text, chunk_size=4000, overlap=400):
    chunks = []

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


def detect_sections(text):
    """
    Detect section headings throughout the extracted PDF text.
    Returns a list of (section_name, section_text) pairs.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return [("General", "")]

    # Common section heading patterns
    heading_pattern = re.compile(
        r"^(Introduction|Data Collection|Data Analysis|Risk Management|"
        r"Conclusion|Overview|Summary|Methodology|Results|Discussion|"
        r"Financial Analysis|Company Overview|Financial Statements|"
        r"Revenue|Expenses|Profit|References)$",
        re.IGNORECASE
    )

    sections = []
    current_section = "General"
    current_lines = []

    for line in lines:

        # Check whether this line is a section heading
        if heading_pattern.match(line):

            # Save previous section
            if current_lines:
                sections.append(
                    (current_section, "\n".join(current_lines).strip())
                )

            # Start new section
            current_section = line
            current_lines = []

        else:
            current_lines.append(line)

    # Save final section
    if current_lines:
        sections.append(
            (current_section, "\n".join(current_lines).strip())
        )

    return sections


@tool
def process_pdf(file_path):
    """
    Read a financial PDF, extract text, detect sections,
    create chunks, and return section-wise JSON.
    """

    pages = read_pdf(file_path)

    sections = {}

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        if not text.strip():
            continue

        detected_sections = detect_sections(text)

        for section_name, section_text in detected_sections:

            if section_name not in sections:
                sections[section_name] = {
                    "pages": [],
                    "chunks": []
                }

            if page_number not in sections[section_name]["pages"]:
                sections[section_name]["pages"].append(page_number)

            chunks = chunk_text(section_text)

            for chunk in chunks:
                sections[section_name]["chunks"].append(chunk)

    result = {
        "filename": file_path,
        "file_type": "application/pdf",
        "page_count": len(pages),
        "section_count": len(sections),
        "sections": sections
    }

    return json.dumps(result, indent=2)


document_agent = Agent(
    role="Financial Document Processing Specialist",

    goal=(
        "Process uploaded financial documents and prepare "
        "section-wise structured data for downstream analysis."
    ),

    backstory=(
        "You are responsible for processing financial documents. "
        "You validate documents, extract their content, identify "
        "sections, and prepare clean structured information for "
        "the next financial analysis agents."
    ),

    tools=[process_pdf],
    verbose=True,
    allow_delegation=False
)


from crewai import Task


document_task = Task(
    description=(
        "Process the uploaded financial document. "
        "Use the document processing tool to validate the PDF, "
        "extract its text, identify document sections, create chunks, "
        "and organize the extracted information section-wise. "
        "Return the processed document as JSON with sections, "
        "page numbers, and chunks for downstream financial analysis."
    ),

    expected_output=(
        "A valid JSON-formatted representation of the financial "
        "document with the extracted data divided section-wise, "
        "including page numbers and text chunks."
    ),

    agent=document_agent
)


from crewai import Crew


document_crew = Crew(
    agents=[document_agent],
    tasks=[document_task],
    verbose=True
)