from langchain_ollama import OllamaLLM

from get_answer.config import RAGConfig
from get_answer.prompts import build_prompt


class AnswerGenerator:
    def __init__(self, config: RAGConfig) -> None:
        llm = OllamaLLM(
            model=config.llm_model_name,
            temperature=config.llm_temperature,
        )
        self._max_context_chars = config.max_context_chars
        self._chain = build_prompt() | llm

    def get_llm_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return "Не удалось найти релевантные фрагменты в базе знаний для ответа на вопрос."

        return self._chain.invoke(
            {
                "context": context[: self._max_context_chars],
                "question": question,
            }
        )
