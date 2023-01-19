# usr/bin/env bash
docker-compose exec backend python manage.py makemigrations users
docker-compose exec backend python manage.py migrate users
docker-compose exec backend python manage.py makemigrations recipes
docker-compose exec backend python manage.py migrate recipes
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
# docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input 
docker-compose exec backend python manage.py load_ingredients_data
# gunicorn foodgram.wsgi:application --bind 0:8000
python manage.py runserver 0.0.0.0:8000