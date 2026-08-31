import asyncio

from agents.Single_Extraction_agent import ExtractionProcessor


async def test():
    result = await ExtractionProcessor.process_extraction(
        "YOUR_DOCUMENT_ID",
        "Infosys Limited"
    )

    print(result)


asyncio.run(test())