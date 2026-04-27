## test_get_answer

Проект с API для индексации PDF-документов и постановки вопросов по проиндексированному содержимому.

В этом README оставлено подробное описание только сервиса `fastapi_indexer_app`.

## Требования

- установлен и запущен `Ollama`;
- локально запущена модель в `Ollama` (модель, которую использует backend для генерации ответов).

## client

### Запуск в dev

Из папки `client`:

```bash
pnpm install
HOST=127.0.0.1 pnpm dev
```

По умолчанию dev-сервер поднимается на `http://127.0.0.1:5173`.

## fastapi_indexer_app

### Что делает сервис

- принимает PDF через HTTP;
- сохраняет файл в `documents/uploaded`;
- запускает индексацию в фоне и создает Chroma-индекс в `data/chroma/uploaded`;
- хранит метаданные документов и jobs вопросов в DuckDB (`data/documents.duckdb`);
- запускает вопрос к документу в фоне и дает статус/результат через job endpoint.

### Запуск

```bash
uv run uvicorn fastapi_indexer_app.main:app --reload
```

Базовый health-check:

```bash
curl "http://127.0.0.1:8000/health"
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

### Основной сценарий работы

1. Загрузить PDF на индексацию.
2. Периодически проверять статус документа, пока не станет `completed`.
3. Отправить вопрос по `document_id`.
4. Проверять статус вопроса по `job_id`, пока не появится `answer`.

### API: документы

#### `POST /documents/index`

Загружает PDF и создает задачу фоновой индексации.

Пример:

```bash
curl -X POST "http://127.0.0.1:8000/documents/index" \
  -F "file=@documents/your_file.pdf"
```

Возвращает объект документа (`DocumentIndexResponse`) со статусом `pending`/`processing`/`completed`/`failed`.

#### `GET /documents`

Возвращает список всех документов (новые сверху).

#### `GET /documents/{document_id}`

Возвращает детали конкретного документа по `document_id`.

#### `GET /documents/{document_id}/index-debug`

Диагностика индекса для уже завершенного документа:
- `collection_count`;
- `sample_chunks` (до 2 примеров);
- служебные поля документа.

Если документ еще не завершил индексацию, вернется `409`.

### API: вопросы по документу

#### `POST /documents/{document_id}/ask`

Создает job на генерацию ответа по документу.

Тело запроса:

```json
{
  "question": "О чем документ?",
  "n_results": 8
}
```

- `question` обязателен;
- `n_results` опционален (сколько релевантных чанков извлечь перед генерацией).

Ответ: `202 Accepted` и объект `DocumentQuestionJobResponse`.

#### `GET /documents/ask-jobs/{job_id}`

Возвращает статус и детали job по `job_id`:
- `status` (`pending` / `processing` / `completed` / `failed`);
- `answer` (если готов);
- `error_message` (если ошибка).

#### `GET /documents/{document_id}/ask-jobs/{job_id}`

То же, что endpoint выше, но дополнительно проверяет, что job принадлежит указанному документу.

### Где хранятся данные

- загруженные PDF: `documents/uploaded`;
- индексы Chroma: `data/chroma/uploaded`;
- метаданные документов и jobs: `data/documents.duckdb`.
