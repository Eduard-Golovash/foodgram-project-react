import os
import sys
import django
import csv

from recipes.models import Ingredient


script_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.abspath(os.path.join(script_path, '..'))

sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


csv_file_path = os.path.join(script_path, '..', 'fixtures', 'ingredients.csv')

with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        name, measurement_unit = row
        Ingredient.objects.create(name=name, measurement_unit=measurement_unit)

print("Data loaded successfully.")
