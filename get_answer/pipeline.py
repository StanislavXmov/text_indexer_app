from get_answer.config import RAGConfig
from get_answer.formatter import format_response
from get_answer.generator import AnswerGenerator
from get_answer.retrieval import Retriever


class RAGPipeline:
    def __init__(self, config: RAGConfig) -> None:
        self._config = config
        self._retriever = Retriever(config)
        self._generator = AnswerGenerator(config)

    def enhanced_query_with_llm(self, question: str, n_results: int | None = None) -> str:
        context, documents = self._retriever.retrieve_context(question, n_results)
        answer = self._generator.get_llm_answer(question, context)
        return format_response(question, answer, documents)
