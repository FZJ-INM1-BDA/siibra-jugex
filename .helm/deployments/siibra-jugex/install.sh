#! /bin/bash


helm install jugex .helm/toolbox \
    -f .helm/deployments/siibra-jugex/env.yaml