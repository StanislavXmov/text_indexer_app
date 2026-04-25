from typing import List


def format_response(question: str, answer: str, source_chunks: List[str], max_sources: int = 3) -> str:
    response = f"**Question:** {question}\n\n"
    response += f"**Answer:** {answer}\n\n"
    response += "**Sources:**\n"

    if not source_chunks:
        response += "1. Источники не найдены.\n"
        return response

    for index, chunk in enumerate(source_chunks[:max_sources], 1):
        preview = chunk[:100].replace("\n", " ") + "..."
        response += f"{index}. {preview}\n"

    return response
