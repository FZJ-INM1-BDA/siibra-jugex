FROM python:3.10-slim
RUN pip install -U pip

RUN mkdir /requirements

# install requirements for worker (celery etc)
COPY ./http_wrapper/requirements-worker.txt /requirements/
RUN pip install -r /requirements/requirements-worker.txt

# install requirements for toolbox (numpy, etc)
COPY ./requirements.txt /requirements/requirements.txt
RUN pip install -r /requirements/requirements.txt

# NB
# the path is chosen deliberately to allow for proper config mapping
# modify this at your own peril
COPY . /siibra_toolbox
WORKDIR /siibra_toolbox
RUN pip install .

WORKDIR /siibra_toolbox
USER nobody

ENTRYPOINT celery -A http_wrapper.scheduling.worker.app worker -l INFO
