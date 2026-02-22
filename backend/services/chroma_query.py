def chroma_query(pdf_text: str) -> list[str]:
    """
    Query ChromaDB with the PDF text and return the top-3 most relevant
    knowledge-base chunks.

    Args:
        pdf_text: The full text corpus extracted from the PDF.

    Returns:
        A list of 3 relevant context strings.
    """
    # TODO: replace with real ChromaDB retrieval
    return [
        "Relevant context chunk 1 (stub)",
        "Relevant context chunk 2 (stub)",
        "Relevant context chunk 3 (stub)",
    ]
