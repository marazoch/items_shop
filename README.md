# Django Shop (MVP)

Минимально-рабочий интернет‑магазин на Django: каталог, корзина в БД (по сессии), промокоды, оформление заказа с проверкой остатков (atomic).

## Возможности
- Каталог товаров (категории, товары, активность).
- Корзина хранится в БД, связка по `session_key`.
- Промокоды (процентная скидка, окно действия, флаг активности).
- Оформление заказа: создаёт Order/OrderItem, списывает склад.
- Интерактивность через AJAX `fetch` (POST) с CSRF, состояния сохраняются.

## Стек
- Python 3.12+
- Django 5.x (SQLite по умолчанию)
- Gunicorn (для Docker)

---

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # опционально
python manage.py runserver
```

Зайдите в `/admin/` и создайте категории, товары и (опционально) промокод.

## Docker

```bash
docker compose up --build
# http://127.0.0.1:8000/
```

## URL
- `/` — каталог
- `/product/<slug>/` — карточка товара
- `/cart/` — корзина
- `/api/cart/add/<id>/`, `/api/cart/qty/<id>/`, `/api/cart/apply-coupon/`, `/api/checkout/`

## Быстрые заметки продакшена
- Установите переменные окружения: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`.
- Настройте базу данных (PostgreSQL) и статику (nginx).
- Для внешних клиентов вынесите JSON‑эндпоинты на DRF.
