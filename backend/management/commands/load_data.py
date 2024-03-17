import os
import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Load data from CSV file'

    def handle(self, *args, **options):
        script_path = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_path, '..', '..', 'fixtures', 'ingredients.csv')
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(name=name, measurement_unit=measurement_unit)

        self.stdout.write(self.style.SUCCESS("Data loaded successfully."))