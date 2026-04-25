from pathlib import Path

from markitdown import MarkItDown


def load_document_content(output_folder: str, filename: str) -> tuple[Path, str]:
    file_path = Path(output_folder) / filename
    markdown_converter = MarkItDown()
    result = markdown_converter.convert(file_path)
    return file_path, result.text_content
