import csv
from pathlib import Path
from foodgram.settings import BASE_DIR
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.db.utils import IntegrityError

PROJECT_DIR = Path(BASE_DIR).resolve().joinpath('data')
FILE_TO_OPEN = PROJECT_DIR / "ingredients.csv"


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(FILE_TO_OPEN, 'r', encoding='utf-8') as f:
            data = csv.DictReader(f)
            for ingredient in data:
                try:
                    Ingredient.objects.create(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
                except IntegrityError:
                    print('Ингридиент уже существует')
