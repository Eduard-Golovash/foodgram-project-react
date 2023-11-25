import pandas as pd
from recipes.models import Ingredient

data = pd.read_csv('fixtures/ingredients.csv')

for index, row in data.iterrows():
    Ingredient.objects.create(name=row['name'], measurement_unit=row['measurement_unit'])