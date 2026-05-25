# API Reference

Base URL: `http://localhost:8000`. Все доменные ручки — под префиксом `/api/v1`.

Формат всех ответов и тел — JSON (`Content-Type: application/json`).

Общие коды:

| Код | Значение |
|---|---|
| `200` | успех |
| `201` | ресурс создан |
| `204` | успех, тела нет (DELETE) |
| `400` | нарушено бизнес-правило (например, копия занята) |
| `404` | ресурс не найден |
| `409` | конфликт уникальности (ISBN, email) |
| `422` | невалидный body / query |

Любая `422` имеет стандартный FastAPI-формат:

```json
{"detail": [{"loc": ["body", "field"], "msg": "...", "type": "..."}]}
```

Прочие — `{"detail": "..."}`.

Пагинация для list-эндпойнтов:

| Параметр | Тип | По умолч. | Ограничение |
|---|---|---|---|
| `offset` | int | 0 | `>= 0` |
| `limit` | int | 10 | `1..100` |

Ответ:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 10}
```

---

## Health

### `GET /health`

Проверка живости. Используется healthcheck-ами / мониторингом.

**Ответ 200:**

```json
{"status": "ok"}
```

---

## Authors `/api/v1/authors`

### `GET /api/v1/authors/`

Список авторов с пагинацией.

**Query:** `offset`, `limit` (см. выше).

**Ответ 200:**

```json
{
  "items": [
    {"id": 1, "first_name": "Лев", "last_name": "Толстой", "bio": "..."}
  ],
  "total": 1, "offset": 0, "limit": 10
}
```

### `GET /api/v1/authors/{author_id}`

**Ответ 200:**

```json
{"id": 1, "first_name": "Лев", "last_name": "Толстой", "bio": "..."}
```

**404** — автор не найден.

### `POST /api/v1/authors/`

**Body:**

```json
{"first_name": "Лев", "last_name": "Толстой", "bio": "опционально"}
```

**Ответ 201:** созданный автор. **422** — пустые имя/фамилия.

### `PUT /api/v1/authors/{author_id}`

Частичное обновление: только переданные поля будут изменены.

**Body (любая комбинация):**

```json
{"first_name": "...", "last_name": "...", "bio": "..."}
```

**Ответ 200:** обновлённый объект. **404** — не найден.

### `DELETE /api/v1/authors/{author_id}`

**Ответ 204.** Связь с книгами (`book_authors`) удаляется каскадно. Сами книги остаются.

---

## Books `/api/v1/books`

### `GET /api/v1/books/`

**Query:** `offset`, `limit`, `author_id` (опциональный фильтр).

**Ответ 200:**

```json
{
  "items": [
    {
      "id": 1, "title": "Война и мир", "description": null,
      "isbn": "9785170902231", "year": 1869,
      "authors": [{"id": 1, "first_name": "Лев", "last_name": "Толстой", "bio": "..."}]
    }
  ],
  "total": 1, "offset": 0, "limit": 10
}
```

### `GET /api/v1/books/{book_id}`

Возвращает книгу вместе со списком авторов. **404** — не найдена.

### `POST /api/v1/books/`

**Body:**

```json
{
  "title": "War and Peace",
  "description": "опционально",
  "isbn": "9785170902231",
  "year": 1869,
  "author_ids": [1, 2]
}
```

Несуществующие `author_ids` тихо отбрасываются (валидация автора не делается). `isbn` — unique; повтор → **409**.

**Ответ 201:** созданная книга с заполненным списком `authors`.

### `PUT /api/v1/books/{book_id}`

Частичное обновление. Если передан `author_ids` — список авторов **заменяется** целиком. Чтобы очистить — `"author_ids": []`. Чтобы не трогать — не передавать поле.

**404** — не найдена. **409** — конфликт ISBN.

### `DELETE /api/v1/books/{book_id}`

**Ответ 204.** Каскадно удаляет copies (а через них — связанные loans).

---

## Copies

Экземпляры живут под книгой, поэтому ручки сгруппированы по разным префиксам.

### `GET /api/v1/books/{book_id}/copies`

Список экземпляров книги. Без пагинации — обычно их немного.

**Ответ 200:**

```json
[{"id": 1, "book_id": 1, "status": "available"}]
```

**404** — книги нет.

### `POST /api/v1/books/{book_id}/copies`

Создаёт новый экземпляр для книги. Тело пустое.

**Ответ 201:**

```json
{"id": 2, "book_id": 1, "status": "available"}
```

**404** — книги нет.

### `DELETE /api/v1/copies/{copy_id}`

**Ответ 204.** Каскадно удаляет связанные loans. **404** — копии нет.

---

## Readers `/api/v1/readers`

### `GET /api/v1/readers/`

Список читателей с пагинацией.

### `GET /api/v1/readers/{reader_id}`

**404** — не найден.

### `POST /api/v1/readers/`

**Body:**

```json
{"first_name": "Иван", "last_name": "Петров", "email": "ivan@example.com"}
```

`email` — unique. **409** — дубль email.

### `PUT /api/v1/readers/{reader_id}`

Частичное обновление. **409** — конфликт email.

### `DELETE /api/v1/readers/{reader_id}`

**Ответ 204.** Каскадно удаляет loans читателя (включая активные — копия при этом останется в статусе `borrowed`; если важна корректность статусов, сначала верни книгу).

---

## Loans `/api/v1/loans`

### `GET /api/v1/loans/`

**Query:** `offset`, `limit`, `reader_id`, `copy_id` (оба фильтра опциональны и комбинируются по AND).

**Ответ 200:**

```json
{
  "items": [
    {
      "id": 1, "copy_id": 1, "reader_id": 1,
      "loan_date": "2026-05-22T12:34:56+00:00",
      "return_date": null
    }
  ],
  "total": 1, "offset": 0, "limit": 10
}
```

`return_date == null` означает, что выдача активна.

### `GET /api/v1/loans/{loan_id}`

**404** — не найдена.

### `POST /api/v1/loans/`

Выдать копию читателю.

**Body:**

```json
{"copy_id": 1, "reader_id": 1}
```

Сервер атомарно проверяет:

- копия существует — иначе **400** `"Copy not found"`
- копия в статусе `available` — иначе **400** `"Copy is not available"`
- читатель существует — иначе **400** `"Reader not found"`

При успехе ставит `copy.status = borrowed` и создаёт запись `Loan` с `loan_date = now()`.

**Ответ 201:** созданная выдача.

### `POST /api/v1/loans/{loan_id}/return`

Вернуть копию.

- проставляет `loan.return_date = now()`
- переводит копию в `available`

**Ответ 200:** обновлённая выдача с заполненным `return_date`.

**400** — `"Book already returned"`, если выдача уже закрыта.
**404** — выдача не найдена.

---

## Что не реализовано

Намеренно вне скоупа учебного задания:

- авторизация и роли
- продление и просрочка выдач (нет `due_date`)
- история статусов экземпляра
- поиск по тексту (title, имя автора) — фильтрация только по `author_id`
- мягкое удаление
