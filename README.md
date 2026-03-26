# Config Service

REST API сервис управления конфигурациями для распределённых сервисов.
Стек: Python 3.12, Twisted, Klein, PostgreSQL, PyYAML, Jinja2.

---

## Быстрый старт (Docker)

```bash
docker-compose up --build
```

Сервис поднимется на `http://localhost:8080`. PostgreSQL запускается автоматически, таблица создаётся при старте.

---

## Локальный запуск (без Docker)

### Требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Запущенный PostgreSQL

### Установка uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew
brew install uv
```

### Установка зависимостей

```bash
# Создать виртуальное окружение и установить все зависимости из pyproject.toml
uv sync

# Установить вместе с dev-зависимостями
uv sync --dev
```

### Добавление зависимости

```bash
# Продакшн-зависимость
uv add <package>

# Dev-зависимость
uv add --dev <package>
```

### Переменные окружения

Скопируйте `.env.example` и настройте подключение к БД:

```bash
cp .env.example .env
```

| Переменная    | По умолчанию | Описание              |
|---------------|--------------|-----------------------|
| `DB_HOST`     | `localhost`  | Хост PostgreSQL       |
| `DB_PORT`     | `5432`       | Порт PostgreSQL       |
| `DB_NAME`     | `configs`    | Имя базы данных       |
| `DB_USER`     | `postgres`   | Пользователь          |
| `DB_PASSWORD` | `postgres`   | Пароль                |
| `PORT`        | `8080`       | Порт приложения       |

### Запуск

```bash
export $(cat .env | xargs)
uv run config-service
```

---

## API

### POST `/config/{service}`

Загрузить новую конфигурацию. Тело запроса YAML.

```bash
curl -X POST http://localhost:8080/config/my_service \
  -H "Content-Type: text/yaml" \
  --data-binary @- <<EOF
version: 1
database:
  host: db.local
  port: 5432
features:
  enable_auth: true
EOF
```

Ответ:

```json
{"service": "my_service", "version": 1, "status": "saved"}
```

Если поле `version` не указано — назначается автоматически.

---

### GET `/config/{service}`

Получить актуальную конфигурацию.

```bash
curl http://localhost:8080/config/my_service
```

Получить конкретную версию:

```bash
curl http://localhost:8080/config/my_service?version=1
```

Получить с Jinja2-рендерингом (переменные передаются как query-параметры):

```bash
curl "http://localhost:8080/config/my_service?template=1&user=Alice"
```

---

### GET `/config/{service}/history`

Получить историю версий.

```bash
curl http://localhost:8080/config/my_service/history
```

Ответ:

```json
[
  {"version": 1, "created_at": "2025-08-19T12:00:00"},
  {"version": 2, "created_at": "2025-08-19T13:00:00"}
]
```

---

## Коды ответов

| Код | Причина                              |
|-----|--------------------------------------|
| 200 | Успех                                |
| 400 | Невалидный YAML                      |
| 404 | Сервис или версия не найдены         |
| 409 | Версия уже существует                |
| 422 | Не заполнены обязательные поля       |

---

## Тесты

```bash
uv run pytest
```

---

## Линтинг и типизация

```bash
uv run ruff check src tests
uv run ruff format src tests
uv run mypy src
```
