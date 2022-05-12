FROM python:3.10-slim
RUN pip install -U pip

RUN mkdir -p /siibra_jugex/siibra_jugex_http
COPY ./siibra_jugex_http/requirements-worker.txt /siibra_jugex/siibra_jugex_http/requirements-worker.txt
RUN pip install -r /siibra_jugex/siibra_jugex_http/requirements-worker.txt

COPY ./requirements.txt /siibra_jugex/requirements.txt
RUN pip install -r /siibra_jugex/requirements.txt

COPY . /siibra_jugex
WORKDIR /siibra_jugex

RUN pip install .

USER nobody

ENTRYPOINT celery -A siibra_jugex_http.scheduling.worker.app worker -l INFO
