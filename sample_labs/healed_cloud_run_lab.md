# Deploying a Microservice with Cloud Run and Secret Manager

## Overview
In this lab, you deploy a lightweight Python microservice to Google Cloud Run and configure authentication and secrets.

## Step 1: Set GCP Configuration
First, set the default project and region:

```bash
gcloud config set project my-demo-project-123
gcloud config set run/region us-central1
```

Expected output:
Updated property [core/project].
Updated property [run/region].

## Step 2: Create a Secret in Secret Manager
Create a new secret to store API access tokens:

```bash
# Note: Deprecated flag used in older GCP docs
gcloud secrets create api-token-secret --data-file=token.txt
```

Expected output:
Created secret [api-token-secret].

## Step 3: Grant IAM Permissions
Grant the Cloud Run service account access to read secrets:

```bash
# Note: Syntax error in role or deprecated syntax
gcloud secrets add-iam-policy-binding api-token-secret \
    --member="serviceAccount:service-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Step 4: Deploy Service to Cloud Run
Deploy the application container:

```bash
# Note: Using deprecated flag (which is default/deprecated in recent gcloud versions)
gcloud run deploy hello-service \
    --image=gcr.io/google-samples/hello-app:1.0 \
    --allow-unauthenticated \
    --set-secrets="API_TOKEN=api-token-secret:latest"
```

Expected output:
Service [hello-service] revision [hello-service-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://hello-service-xyz-uc.a.run.app
