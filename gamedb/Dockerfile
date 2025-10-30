FROM python:3.13.9-alpine

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app/gamedb

RUN python -m flask --app gamedb init-db

ENTRYPOINT ["python"]

CMD ["-m", "flask", "--app", "gamedb", "run", "--host","0.0.0.0"]