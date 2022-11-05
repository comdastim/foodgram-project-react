# praktikum_new_diplom

### Описание:

Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Стек технологий:

Python3, Django, Django REST Framework, JWT, Docker, Gunicorn, nginx, GIT

### Установка:
Клонировать репозиторий и перейти в него в командной строке: git clone https://@github.com/comdastim/foodgram-project-react.git

Cоздать виртуальное окружение: python3 -m venv env

Активировать виртуальное окружение: 
source env/bin/activate(для macOS или Linux:) либо source/venv/Scripts/activate (для Windows)

Установить зависимости из файла requirements.txt: 
python3 -m pip install --upgrade pip 
pip install -r requirements.txt

Выполнить миграции: python3 manage.py migrate

Запустить проект: python3 manage.py runserver

### Запуск через Docker

Для работы приложения требуется установка на ваш компьютер Python, Docker, PostgreSQL.

Склонировать репозиторий:

git clone git@github.com:comdastim/infra_sp2.git

Запустить docker-compose:

docker-compose up -d

Выполнить миграции:

docker-compose exec web python manage.py migrate —noinput

Выполнить сбор статических файлов:

docker-compose exec web python manage.py collectstatic —no-input

Создать суперпользователя:

docker-compose exec web python manage.py createsuperuser

Скачать образ из репозитория на DockerHub:

docker pull daffna/infra


### Техническое описание проекта:

По адресу http://localhost/api/docs/redoc.html можно найти документацию, в которой описаны примеры возможных запросов к API и структура ожидаемых ответов.

