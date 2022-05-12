# viewer plugin builder
FROM node:16-alpine as builder

COPY ./siibra_jugex_viewerplugin /siibra_jugex_viewerplugin
WORKDIR /siibra_jugex_viewerplugin
RUN mkdir -p public/build
RUN npm i
RUN npm run build

# server image
FROM python:3.10-alpine
RUN pip install -U pip

COPY ./siibra_jugex_http /siibra_jugex_http
WORKDIR /siibra_jugex_http

COPY ./examples /examples

RUN pip install -r ./requirements-server.txt
COPY --from=builder /siibra_jugex_viewerplugin/public /siibra_jugex_http/public
ENV SIIBRA_JUGEX_STATIC_DIR=/siibra_jugex_http/public

USER nobody
EXPOSE 6001
ENTRYPOINT uvicorn main:app --port 6001 --host 0.0.0.0
