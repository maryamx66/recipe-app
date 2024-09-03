FROM python:3.12-slim-bullseye

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD [ "gunicorn", "-w", "2", "app:app" ]