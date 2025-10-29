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
---

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_shop
python manage.py createsuperuser  # опционально
python manage.py runserver
```

Зайдите в `/admin/` и создайте категории, товары и (опционально) промокод.

## Docker

```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
# (опционально)
docker compose exec web python manage.py collectstatic --noinput

```

## URL
- `/` — каталог
- `/product/<slug>/` — карточка товара
- `/cart/` — корзина
- `/api/cart/add/<id>/`, `/api/cart/qty/<id>/`, `/api/cart/apply-coupon/`, `/api/checkout/`

