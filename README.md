# Library Management API

REST API для небольшой библиотеки: авторы, книги, физические экземпляры (copies), читатели и выдачи (loans).

Стек: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 18, Alembic, Pydantic v2. Python 3.12.

API после запуска: `http://localhost:8000`. Swagger UI: `http://localhost:8000/docs`. ReDoc: `http://localhost:8000/redoc`.

---

## Быстрый старт (Windows)

Нужен только **Docker Desktop**. Питон ставить не надо.

### 1. Установка Docker Desktop

- Скачать с [docker.com](https://www.docker.com/products/docker-desktop/), поставить, перезагрузиться.
- При первом запуске инсталлер предложит включить **WSL2** — согласиться. Docker на винде работает поверх WSL2.
- После старта в трее должен висеть зелёный кит — без него ничего не поднимется.

### 2. Распаковать архив

Если пришёл `library-project.zip` — распаковать через правый клик → «Извлечь всё...». Получится папка `library-project/`.

Если репозиторий — `git clone <ссылка> && cd library-project`.

> В архиве `.sh`-скрипты лежат с LF-окончаниями строк, как нужно для Linux-контейнеров. Открывать их в Notepad и пересохранять не надо.

### 3. Поднять стек

В PowerShell в папке проекта:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Первый запуск ~1–2 минуты (тянет образы python и postgres). При старте контейнер сам прогоняет миграции — отдельно ничего запускать не надо.

### 4. Проверить

```powershell
curl.exe http://localhost:8000/health
# {"status":"ok"}
```

> Важно: в PowerShell `curl` — это alias на `Invoke-WebRequest`, у него другой синтаксис. Везде ниже используй именно **`curl.exe`** (он есть в Windows 10/11 из коробки).

Открыть в браузере: `http://localhost:8000/docs` — Swagger UI.

### 5. Залить демо-данные (опционально)

```powershell
docker compose exec app python scripts/seed.py
```

### 6. Прогнать тесты

```powershell
docker compose exec app pytest tests/ -v
```

### Остановить и запустить заново

```powershell
docker compose down            # стоп
docker compose up -d            # старт без ребилда
docker compose down -v          # стоп + удалить том БД (полный сброс)
```

### Если хочется make (опционально)

`make` короче, но не обязателен. Поставить через [Chocolatey](https://chocolatey.org/install):

```powershell
choco install make
```

Дальше работает `make up`, `make seed`, `make test` и т.д. Полный список — `make help`.

---

## Быстрый старт (Linux / macOS)

```bash
cp .env.example .env
make up         # docker compose up -d --build
make seed       # опционально
make test
```

Если нет make — используй прямые docker-команды, они эквивалентны (см. `Makefile`).

---

## Команды

| Команда | Что делает |
|---|---|
| `make up` | поднять db + app, прогнать миграции |
| `make down` | остановить контейнеры |
| `make restart` | рестартануть только app |
| `make logs` | tail логов приложения |
| `make migrate` | применить миграции вручную |
| `make seed` | залить демо-данные (см. `scripts/seed.py`) |
| `make test` | прогнать все тесты внутри контейнера |
| `make test-file FILE=tests/test_loans.py` | конкретный файл |
| `make shell` | bash внутри app-контейнера |
| `make psql` | psql внутри db-контейнера |
| `make reset` | down + удалить том БД (потеря данных) |
| `make build-local` | создать `.venv` локально (для IDE-подсветки) |

---

## Тесты

```bash
make test
```

Тесты гоняются **внутри app-контейнера** против отдельной БД `library_test`. Боевые данные не трогаются. Тестовая БД создаётся автоматически при первом старте (`scripts/init-db.sh`) либо on-the-fly из `tests/conftest.py`.

---

## Локальная разработка без Docker

Если хочется запускать app или тесты прямо с хоста (для дебага в IDE):

```bash
make build-local
source .venv/bin/activate     # на Windows: .venv\Scripts\activate
docker compose up -d db        # нужен только Postgres
alembic -c migrations/alembic.ini upgrade head
uvicorn app.main:app --reload
```

`DATABASE_URL` уже указывает на `localhost:5432`, так что подключение сработает.

---

## Структура проекта

```
app/
  main.py          FastAPI app, регистрация роутеров, IntegrityError → 409
  database.py      async engine, sessionmaker, get_db()
  models.py        SQLAlchemy 2.0 declarative models
  schemas.py       Pydantic v2 (Create / Update / Read + PaginatedResponse)
  crud.py          работа с БД, без HTTP-зависимостей
  routers/         по одному роутеру на ресурс
migrations/        Alembic (async env.py)
tests/             pytest-asyncio + httpx
scripts/
  entrypoint.sh    миграции + uvicorn (запускается в контейнере)
  init-db.sh       создание library_test при первом старте Postgres
  seed.py          демо-данные
```

Слои: роутер валидирует HTTP и переводит доменные ошибки в коды; `crud.py` ничего не знает про FastAPI и работает только с `AsyncSession`.

## Доменная модель

- **Author** ↔ **Book** — M:M через `book_authors`
- **Book** 1—N **Copy** (физический экземпляр, статус `available` / `borrowed`)
- **Reader** 1—N **Loan**
- **Copy** 1—N **Loan** — у одного экземпляра может быть много исторических выдач, но активной — не больше одной

Все FK на стороне БД с `ondelete="CASCADE"`, в моделях коллекции помечены `passive_deletes=True`, чтобы SQLAlchemy не пытался занулять FK перед удалением (это сделает сам Postgres).

## Эндпойнты

Все ресурсы под префиксом `/api/v1`. Пагинация — `?offset=` (≥ 0) и `?limit=` (1..100), ответ — `{items, total, offset, limit}`.

Подробная документация по каждой ручке: [`docs/API.md`](docs/API.md).

Краткий список:

- `GET /health`
- `/api/v1/authors` — CRUD
- `/api/v1/books` — CRUD, фильтр `?author_id=`
- `/api/v1/books/{book_id}/copies` — список / создание экземпляра
- `/api/v1/copies/{copy_id}` — удаление экземпляра
- `/api/v1/readers` — CRUD
- `/api/v1/loans` — список (фильтры `?reader_id=`, `?copy_id=`), создание, возврат `POST /{id}/return`

### Коды ошибок

| Код | Когда |
|---|---|
| 400 | бизнес-правило нарушено (копия занята, читатель не существует, возврат уже сделан) |
| 404 | ресурс не найден |
| 409 | нарушение unique-ограничения (дублирующийся ISBN / email) |
| 422 | невалидное тело или query-параметр (валидация Pydantic) |

---

## Пример сценария (curl)

```bash
BASE=http://localhost:8000/api/v1

curl -X POST $BASE/authors/ -H 'content-type: application/json' \
  -d '{"first_name":"Lev","last_name":"Tolstoy"}'

curl -X POST $BASE/books/ -H 'content-type: application/json' \
  -d '{"title":"War and Peace","year":1869,"author_ids":[1]}'

curl -X POST $BASE/books/1/copies

curl -X POST $BASE/readers/ -H 'content-type: application/json' \
  -d '{"first_name":"Ivan","last_name":"Ivanov","email":"ivan@example.com"}'

curl -X POST $BASE/loans/ -H 'content-type: application/json' \
  -d '{"copy_id":1,"reader_id":1}'

curl -X POST $BASE/loans/1/return
```

## Конфигурация

`.env`:

```
DATABASE_URL=postgresql+asyncpg://library:library@localhost:5432/library
TEST_DATABASE_URL=postgresql+asyncpg://library:library@localhost:5432/library_test
```

Внутри Docker эти значения переопределяются на хост `db` (см. `docker-compose.yml`). Настройки читаются через `pydantic-settings`, посторонние ключи игнорируются.

---

## Troubleshooting

**`port is already allocated`** при `make up` — на 5432 уже сидит локальный Postgres. Останови его или поменяй маппинг в `docker-compose.yml` на `"5433:5432"`.

**`make test` падает с `database "library_test" does not exist`** — это значит, что Postgres-volume старый, init-скрипт не запускался. Сделай `make reset` (снесёт данные!) либо создай руками:

```bash
make psql
CREATE DATABASE library_test;
\q
```

**На Windows `make` не найден** — поставь `choco install make` или работай напрямую через `docker compose ...` (команды в `Makefile`).

**Контейнер app перезапускается в логах** — обычно либо миграция упала (смотри `make logs`), либо БД ещё не готова. healthcheck должен отрабатывать, но если что — `make down && make up`.

**На Windows: `./scripts/entrypoint.sh: /bin/sh^M: bad interpreter`** — `.sh` склонировался с CRLF. Не должно случиться благодаря `.gitattributes`, но если — конвертируй вручную:

```powershell
docker run --rm -v ${PWD}:/repo alpine sh -c "apk add --no-cache dos2unix && dos2unix /repo/scripts/*.sh"
docker compose up -d --build
```

**На Windows: `curl: Invoke-WebRequest ...` с ошибкой парсинга** — это PowerShell-алиас. Используй `curl.exe` (с расширением).
#   l i b r a r y  
 