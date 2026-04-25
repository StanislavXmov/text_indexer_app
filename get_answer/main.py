import time

from get_answer.config import RAGConfig
from get_answer.pdf_export import create_pdf
from get_answer.sample_data import SAMPLE_TEXT


def main() -> None:
    start_time = time.perf_counter()
    config = RAGConfig()

    # If you need RAG query flow, uncomment:
    # from get_answer.pipeline import RAGPipeline
    # pipeline = RAGPipeline(config)
    # question = "закрытая часть Электронной площадки «Фабрикант» что это такое?"
    # response = pipeline.enhanced_query_with_llm(question)
    # print(response)

    create_pdf(SAMPLE_TEXT, config.output_pdf_path, config)

    elapsed_time = time.perf_counter() - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()
