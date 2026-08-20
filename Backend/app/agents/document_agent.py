from crewai import Agent
from crewai.tools import tool

from pypdf import PdfReader

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


@tool
def process_pdf(file_path):
    """Read a financial PDF, extract its text, create chunks, and return metadata."""
    
    pages = read_pdf(file_path)

    all_chunks = []

    for page in pages:
        chunks = chunk_text(page["text"])

        for chunk in chunks:
            all_chunks.append({
                "page_number": page["page_number"],
                "text": chunk
            })

    metadata = create_metadata(
        file_path,
        pages,
        all_chunks
    )

    return {
        "pages": pages,
        "chunks": all_chunks,
        "metadata": metadata
    }

def create_metadata(file_path, pages, chunks):
    return {
        "filename": file_path,
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "file_type": "application/pdf"
    }

document_agent = Agent(
    role="Financial Document Processing Specialist",
    goal="Process uploaded financial documents and prepare them for downstream analysis.",
    backstory=(
        "You are responsible for processing financial documents. "
        "You validate documents, understand their content, and prepare "
        "clean information for the next financial analysis agents."
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
    "extract its text, create chunks, and generate metadata. "
    "Return the parsed document information, chunks, and metadata "
    "for downstream financial analysis."
    ),
    expected_output=(
        "Clean and structured information from the uploaded "
        "financial document, ready for downstream analysis."
    ),
    agent=document_agent
)

from crewai import Crew


document_crew = Crew(
    agents=[document_agent],
    tasks=[document_task],
    verbose=True
)