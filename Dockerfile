FROM python:3.12-slim as base

FROM base AS builder

WORKDIR /app

RUN pip3 install --no-cache-dir --upgrade pipenv

COPY Pipfile Pipfile.lock ./

RUN export PIPENV_VENV_IN_PROJECT=1 && pipenv install --deploy

COPY src ./src/

FROM base

HEALTHCHECK NONE

EXPOSE 80

RUN apt-get -y update && apt-get -y upgrade && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pipenv

WORKDIR /app

COPY --from=builder /app /app

ENTRYPOINT ["bash", "-c", "pipenv run start-server"]
