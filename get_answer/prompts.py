from langchain_core.prompts import PromptTemplate


RAG_PROMPT_TEMPLATE = """Опираясь на предоставленную документацию, ответьте на вопрос чётко и точно.

Documentation:
{context}

Question: {question}

Answer (будьте точны в отношении синтаксиса, ключевых слов и приведите примеры):"""


def build_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["context", "question"],
        template=RAG_PROMPT_TEMPLATE,
    )
