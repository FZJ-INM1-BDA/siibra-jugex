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

RUN mkdir -p /siibra_jugex
COPY ./siibra_jugex_http/requirements-server.txt /siibra_jugex/requirements-server.txt
RUN pip install -r /siibra_jugex/requirements-server.txt

COPY ./siibra_jugex_http /siibra_jugex/siibra_jugex_http
COPY ./examples /siibra_jugex/examples
WORKDIR /siibra_jugex/

COPY --from=builder /siibra_jugex_viewerplugin/public /siibra_jugex/siibra_jugex_http/public
ENV SIIBRA_JUGEX_STATIC_DIR=/siibra_jugex/siibra_jugex_http/public

USER nobody
EXPOSE 6001
ENTRYPOINT uvicorn siibra_jugex_http.main:app --port 6001 --host 0.0.0.0
