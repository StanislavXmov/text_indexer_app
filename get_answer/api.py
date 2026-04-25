from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(title="Test Get Answer API")


@app.get("/", response_class=HTMLResponse)
def test_page() -> str:
    return """
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>FastAPI Test Page</title>
      </head>
      <body style="font-family: Arial, sans-serif; margin: 2rem;">
        <h1>FastAPI подключен</h1>
        <p>Тестовая страница работает корректно.</p>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
