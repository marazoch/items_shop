from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import Category, Product, Coupon

class Command(BaseCommand):
    help = "Наполняет базу тестовыми категориями, товарами и купонами"

    def handle(self, *args, **options):
        now = timezone.now()
        # Категории
        cat_data = [
            ("Одежда", "clothes"),
            ("Обувь", "shoes"),
            ("Аксессуары", "accessories"),
        ]
        cats = {}
        for name, slug in cat_data:
            c, _ = Category.objects.get_or_create(name=name, slug=slug)
            cats[slug] = c

        # Товары
        products = [
            (cats["clothes"], "Футболка Basic белая", "tshirt-basic-white", "999.00", 120),
            (cats["clothes"], "Футболка Basic чёрная", "tshirt-basic-black", "999.00", 110),
            (cats["clothes"], "Худи Oversize серое", "hoodie-oversize-grey", "2990.00", 60),
            (cats["clothes"], "Худи с молнией", "hoodie-zip", "3290.00", 45),
            (cats["clothes"], "Свитшот унисекс", "sweatshirt-unisex", "2490.00", 50),
            (cats["clothes"], "Джинсы Straight Fit", "jeans-straight", "3990.00", 35),
            (cats["clothes"], "Джинсы Slim Fit", "jeans-slim", "4190.00", 32),
            (cats["clothes"], "Рубашка Oxford белая", "shirt-oxford-white", "2190.00", 40),

            (cats["shoes"], "Кроссовки Runner Light", "sneakers-runner-light", "4590.00", 70),
            (cats["shoes"], "Кеды Canvas Low", "sneakers-canvas-low", "2990.00", 90),
            (cats["shoes"], "Ботинки Trek Waterproof", "boots-trek-waterproof", "6990.00", 25),
            (cats["shoes"], "Сандалии Comfort", "sandals-comfort", "2490.00", 40),

            (cats["accessories"], "Рюкзак Urban 20L", "backpack-urban-20l", "3490.00", 55),
            (cats["accessories"], "Сумка поясная", "waist-bag-classic", "1490.00", 100),
            (cats["accessories"], "Кепка Cotton", "cap-cotton", "990.00", 140),
            (cats["accessories"], "Шапка Rib Knit", "beanie-rib-knit", "1290.00", 80),
            (cats["accessories"], "Ремень кожаный", "belt-leather", "1990.00", 60),
            (cats["accessories"], "Носки (3 пары)", "socks-3pack", "590.00", 200),
        ]
        created = 0
        for category, name, slug, price, qty in products:
            obj, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": category,
                    "name": name,
                    "price": price,
                    "quantity": qty,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Создано товаров: {created}"))

        # Купоны
        Coupon.objects.get_or_create(
            code="WELCOME10",
            defaults=dict(percent_off=10, active=True,
                          valid_from=now.replace(year=2025, month=1, day=1, hour=0, minute=0, second=0),
                          valid_to=now.replace(year=2026, month=12, day=31, hour=23, minute=59, second=59))
        )
        Coupon.objects.get_or_create(
            code="SALE20",
            defaults=dict(percent_off=20, active=True,
                          valid_from=now.replace(year=2025, month=1, day=1, hour=0, minute=0, second=0),
                          valid_to=now.replace(year=2026, month=12, day=31, hour=23, minute=59, second=59))
        )
        self.stdout.write(self.style.SUCCESS("Купоны готовы: WELCOME10, SALE20"))
        self.stdout.write(self.style.SUCCESS("Готово!"))
