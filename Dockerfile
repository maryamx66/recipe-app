FROM python:3.12-slim-bullseye

WORKDIR /app
COPY . .
RUN python3 -m pip install -r requirements.txt

CMD [ "gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app" ]