import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Loading ingredients from csv.'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', type=str)

    def handle(self, *args, **options):
        with open(
            os.path.join(
                DATA_ROOT, options['filename']), 'r', encoding='utf-8'
        ) as f:
            data = csv.load(f)
            for ingredient in data:
                try:
                    Ingredient.objects.create(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit'])
                except IntegrityError:
                    print('Ингридиент уже существует')
