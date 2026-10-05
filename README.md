<div align="center">

# 💳 RestWallets

### Асинхронный REST API для управления электронными кошельками

Создавайте кошельки, пополняйте и снимайте средства, проверяйте баланс.
FastAPI · PostgreSQL · SQLAlchemy · Alembic · Docker Compose

</div>

---

## ✨ Возможности

- Создание кошелька с нулевым балансом.
- Пополнение и снятие средств с блокировкой кошелька на время операции.
- Проверка баланса и обработка ошибок — кошелёк не найден или недостаточно средств.
- Автоматическое применение миграций при запуске приложения в Docker.
- Интерактивная документация API на Swagger UI.

## 🚀 Быстрый запуск

Понадобится установленный [Docker Compose](https://docs.docker.com/compose/).

```bash
git clone https://github.com/illuminatedbylight/RestWallets.git
cd RestWallets
docker compose up --build
```

При первом запуске Docker соберёт образ API и запустит PostgreSQL. Приложение
дождётся готовности базы данных, применит миграции и откроет API на порту `8000`.

| Сервис | Адрес |
| --- | --- |
| REST API | <http://localhost:8000> |
| Swagger UI | <http://localhost:8000/docs> |
| ReDoc | <http://localhost:8000/redoc> |
| PostgreSQL | `localhost:5432` |

Остановить сервисы можно сочетанием `Ctrl+C`. Для запуска в фоне используйте
`docker compose up --build -d`, а для остановки — `docker compose down`.
Данные PostgreSQL хранятся в Docker volume `postgres_data` и сохраняются между
перезапусками. Чтобы удалить также данные БД, выполните
`docker compose down -v`.

> В compose-файле заданы простые учётные данные для локальной разработки.
> Не используйте их в production.

## 📡 API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `POST` | `/api/v1/wallets` | Создать кошелёк |
| `POST` | `/api/v1/wallets/{wallet_uuid}/operation` | Выполнить операцию |
| `GET` | `/api/v1/wallets/{wallet_uuid}` | Получить баланс |

### Пример работы

Создайте кошелёк:

```bash
curl -X POST http://localhost:8000/api/v1/wallets
```

В ответе придут `wallet_id` и начальный баланс. Подставьте этот идентификатор
в запрос на пополнение:

```bash
curl -X POST http://localhost:8000/api/v1/wallets/<wallet_id>/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type":"DEPOSIT","amount":"100.00"}'
```

Для снятия средств укажите `"operation_type":"WITHDRAW"`. Сумма должна быть
положительной; снять больше доступного баланса нельзя.

Проверить баланс:

```bash
curl http://localhost:8000/api/v1/wallets/<wallet_id>
```

## 🧑‍💻 Локальная разработка

Нужны Python 3.12+ и доступный PostgreSQL. Следующие значения подключения
используются приложением по умолчанию и соответствуют конфигурации Compose:

```text
postgresql+asyncpg://wallet_user:wallet_password@localhost:5432/wallet_db
```

Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Запустите PostgreSQL через Compose:

```bash
docker compose up -d postgres
```

Примените миграции и запустите API:

```bash
alembic upgrade head
uvicorn main:app --reload
```

Если база данных доступна по другому адресу, задайте переменную окружения
`DATABASE_URL` в формате SQLAlchemy async, например:

```bash
export DATABASE_URL='postgresql+asyncpg://user:password@localhost:5432/wallet_db'
```

## 🧪 Тесты

Тесты используют отдельную базу `wallet_test_db` на том же PostgreSQL-сервере.
Если она ещё не создана, запустите PostgreSQL командой из раздела локальной
разработки и создайте базу:

```bash
docker compose exec postgres createdb -U wallet_user wallet_test_db
```

Затем выполните:

```bash
pytest
```
