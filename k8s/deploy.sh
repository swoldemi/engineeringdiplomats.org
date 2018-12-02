#!/bin/bash

set -e

# Activate service account used for GCP and set project config
gcloud auth activate-service-account --key-file=gcp-creds.json
gcloud --quiet config set project $GCP_PROJECT_ID
gcloud --quiet config set compute/zone $COMPUTE_ZONE

# Build new image and push to private registry
docker build -t gcr.io/$GCP_PROJECT_ID/engineeringdiplomats.org:latest .
docker login -u _json_key -p "$(cat gcp-creds.json)" https://gcr.io
docker push gcr.io/$GCP_PROJECT_ID/engineeringdiplomats.org:latest

# Update all pods on cluster
kubectl set image deployments/engineeringdiplomats engineeringdiplomats=gcr.io/$GCP_PROJECT_ID/engineeringdiplomats.org:latest