# viewer plugin builder
# uncomment if plugin is required

FROM node:16-alpine as builder
COPY ./viewer_plugin /viewer_plugin
WORKDIR /viewer_plugin
RUN mkdir -p public/build
RUN npm i
RUN npm run build

# server image
FROM python:3.10-alpine
RUN pip install -U pip

RUN mkdir /requirements
COPY ./http_wrapper/requirements-server.txt /requirements/
RUN pip install -r /requirements/requirements-server.txt


# NB
# the path is chosen deliberately to allow for proper config mapping
# modify this at your own peril
COPY . /siibra_toolbox
WORKDIR /siibra_toolbox

# copy built artefact to deployment
# uncomment if plugin is required

COPY --from=builder /viewer_plugin/public /siibra_toolbox/public
ENV SIIBRA_TOOLBOX_VIEWER_PLUGIN_STATIC_DIR=/siibra_toolbox/public

USER nobody
EXPOSE 6001
ENTRYPOINT uvicorn http_wrapper.server:app --port 6001 --host 0.0.0.0
