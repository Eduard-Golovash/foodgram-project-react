import os
import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из файла JSON'

    def handle(self, *args, **options):
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', '..', 'fixtures', 'ingredients.json')
        with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                Ingredient.objects.create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'])
        self.stdout.write(
            self.style.SUCCESS("Данные успешно загружены"))
