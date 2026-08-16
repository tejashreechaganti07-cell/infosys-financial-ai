import asyncio
from crewai import Agent, Task
from crewai.tools import tool
from .processor import DocumentProcessor

@tool
def process_document_tool(document_id: str, grid_fs_id: str) -> str:
    """
    Triggers the complete backend document processing pipeline.
    It fetches the PDF from GridFS, extracts text, detects sections, extracts tables,
    chunks the text, generates embeddings, and saves everything to MongoDB.
    Returns a summary of the processed document on success.
    """
    try:
        # Run the async processor synchronously for the CrewAI tool
        # If the environment already has an event loop running, we use get_event_loop
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            result = loop.run_until_complete(DocumentProcessor.process_document(document_id, grid_fs_id))
        except RuntimeError:
            result = asyncio.run(DocumentProcessor.process_document(document_id, grid_fs_id))
            
        return (
            f"Successfully processed document {document_id}. "
            f"Status: {result.status}. "
            f"Extracted {result.page_count} pages, "
            f"{result.tables_detected} tables, and "
            f"stored {result.chunks_created} chunks with {result.embeddings_created} embeddings."
        )
    except Exception as e:
        return f"Document processing failed for {document_id}: {str(e)}"

document_agent = Agent(
    role="Financial Document Processing Specialist",
    goal="Ensure uploaded financial documents are fully processed, structured, and securely stored for downstream analysis.",
    backstory=(
        "You are responsible for processing financial documents. "
        "You validate documents, understand their content, and trigger the "
        "document processing pipeline to extract tables, chunks, and metadata."
    ),
    tools=[process_document_tool],
    verbose=True,
    allow_delegation=False
)

def create_document_task(document_id: str, grid_fs_id: str) -> Task:
    return Task(
        description=(
            f"Process the uploaded financial document with ID: {document_id} and GridFS ID: {grid_fs_id}. "
            "Use the 'process_document_tool' to run the pipeline, which will validate the PDF, "
            "extract text, create chunks, and generate metadata. "
            "Return the summary of the processing results."
        ),
        expected_output="A summary string confirming successful processing and storage of document chunks.",
        agent=document_agent
    )
