from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Breed, Pet, Species


class Command(BaseCommand):
    help = "Добавляет вымышленные записи для демонстрации каталога."

    @transaction.atomic
    def handle(self, *args, **options):
        cat, _ = Species.objects.get_or_create(name="Кошка")
        dog, _ = Species.objects.get_or_create(name="Собака")
        siberian, _ = Breed.objects.get_or_create(name="Сибирская", species=cat)
        labrador, _ = Breed.objects.get_or_create(name="Лабрадор", species=dog)
        examples = [
            ("Персик", siberian, 4, 12000, "Рыжий котёнок"),
            ("Буся", siberian, 6, 15000, "Серая кошка"),
            ("Милка", siberian, 5, 14000, "Белая кошка"),
            ("Бублик", labrador, 3, 26000, "Палевый щенок"),
            ("Рада", labrador, 7, 21000, "Чёрная собака"),
            ("Тоша", labrador, 6, 23000, "Шоколадный щенок"),
        ]
        for name, breed, age, price, description in examples:
            if not Pet.objects.filter(name=name, breed=breed).exists():
                Pet.objects.create(
                    name=name, breed=breed, age_months=age, price=price, description=description,
                )
        self.stdout.write(self.style.SUCCESS("Демонстрационный каталог готов."))
