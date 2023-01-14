FROM python:3.7-slim
WORKDIR /app
COPY ./ /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
CMD ["python3", "manage.py", "runserver", "0:8000"] 
#CMD ["bash", "./entrypoint.sh"]
# миграции, сбор статики
# CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]