#! /bin/bash

helm upgrade jugex .helm/toolbox \
    --reuse-values \
    -f .helm/deployments/siibra-jugex/env.yaml \
    --history-max 3
