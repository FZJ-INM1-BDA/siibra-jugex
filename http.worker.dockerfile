FROM python:3.10-slim
RUN pip install -U pip

COPY . /siibra_jugex
WORKDIR /siibra_jugex
RUN pip install -r ./siibra_jugex_http/requirements-worker.txt

RUN pip install .

WORKDIR /siibra_jugex/siibra_jugex_http
USER nobody

ENTRYPOINT celery -A scheduling.worker.app  worker -l INFO
