import argparse
from dataclasses import replace

from get_answer.config import RAGConfig
from get_answer.pipeline import RAGPipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask a question against a Chroma index.")
    parser.add_argument(
        "--question",
        "-q",
        required=True,
        help="Question to ask.",
    )
    parser.add_argument(
        "--chroma-path",
        required=True,
        help="Path to the indexed Chroma database directory.",
    )
    parser.add_argument(
        "--collection-name",
        required=False,
        default=None,
        help="Chroma collection name. If omitted, default from config is used.",
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=None,
        help="How many relevant chunks to retrieve (default from config).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    default_config = RAGConfig()
    config = replace(
        default_config,
        chroma_path=args.chroma_path,
        collection_name=args.collection_name or default_config.collection_name,
    )
    pipeline = RAGPipeline(config)
    response = pipeline.enhanced_query_with_llm(args.question, args.n_results)
    print(response)


if __name__ == "__main__":
    main()
