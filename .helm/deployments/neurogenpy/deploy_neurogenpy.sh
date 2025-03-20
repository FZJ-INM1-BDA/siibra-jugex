#! /bin/bash

SERVER_IMG="docker-registry.ebrains.eu/siibra-toolbox/neurogenpy"
WORKER_IMG="docker-registry.ebrains.eu/siibra-toolbox/neurogenpy"
SERVER_TAG="server"
WORKER_TAG="worker"

helm install neurogenpy ./toolbox \
    --set image.serverRepository=$SERVER_IMG \
    --set image.workerRepository=$WORKER_IMG \
    --set image.serverTag=$SERVER_TAG \
    --set image.workerTag=$WORKER_TAG \
    --set workerResources.limits.memory=4Gi \
    --set envObj.NEUROGENPY_CELERY_BROKER=redis://redis:6379 \
    --set envObj.NEUROGENPY_CELERY_RESULT=redis://redis:6379
    