## test_get_answer

Небольшой тестовый проект на FastAPI.

Что делает:

- поднимает HTTP API;
- отдает простую HTML-страницу на `GET /` (проверка, что приложение работает);
- предоставляет endpoint `GET /health`, который возвращает `{"status": "ok"}` для health-check.

Запуск в режиме разработки:

`uv run uvicorn get_answer.api:app --reload`

`uv run uvicorn fastapi_indexer_app.main:app --reload`
`curl -X POST "http://127.0.0.1:8000/documents/index" -F "file=@documents/your_file.pdf"`

## Индексация документа (создание индекса)

1. Положите PDF в папку `documents/`, например `documents/book.pdf`.
2. (Опционально, для более стабильной/быстрой загрузки моделей) добавьте токен Hugging Face в `.env`:
   - `HF_TOKEN=hf_...`
3. Запустите индексацию:

`uv run python -m set_documents.main --filename book.pdf`

Что произойдет:

- документ будет прочитан и разбит на чанки;
- для чанков будут посчитаны эмбеддинги;
- будет создан новый индекс Chroma в папке вида `data/chroma/set_documents/book_YYYYMMDD_HHMMSS`;
- в конце будет выведен `Collection count: ...`.

Дополнительно можно задать базовую папку для индексов:

`uv run python -m set_documents.main --filename book.pdf --chroma-path ./data/chroma/set_documents`

## Вопрос по проиндексированному документу

После индексации используйте путь к созданной папке индекса:

`uv run python -m get_answer.ask --chroma-path "./data/chroma/set_documents/book_20260425_193504" --question "О чем эта книга?"`

`uv run python -m get_answer.ask --chroma-path "./data/chroma/uploaded/etp_6f99acbf_20260426_111011_6f99acbf" --collection-name "doc_6f99acbfc0a5" --question "О чем этот документ?"`

Полезные опции:

- `--n-results 8` — сколько релевантных чанков извлекать из базы перед генерацией ответа.
- `--collection-name ...` — имя коллекции в Chroma (для загруженных через API документов обязательно указывать).

Пример:

`uv run python -m get_answer.ask --chroma-path "./data/chroma/set_documents/book_20260425_193504" --question "Какие ключевые темы в книге?" --n-results 8`
