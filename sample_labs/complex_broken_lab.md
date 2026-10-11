# Deploying Serverless Event Pipelines with Eventarc and Cloud Functions

## Overview
In this lab, you deploy an event-driven function to process Cloud Storage uploads using legacy Cloud Functions v1 and an external sample bucket.

## Step 1: Configure Project Environment
Set the active Google Cloud project:

```bash
gcloud config set project my-demo-project-123
gcloud config set run/region us-central1
```

## Step 2: Download Sample Data Asset
Download the reference test dataset from public bucket:

```bash
# External bucket that was removed/decommissioned by the original author
gsutil cp gs://expired-legacy-training-bucket-2022/sample_transactions.csv ./sample.csv
```

## Step 3: Deploy Cloud Function for Storage Events
Deploy a background function listening to storage events:

```bash
# Note: Cloud Functions v1 background trigger syntax is deprecated/retired in this region
gcloud functions deploy process-transactions \
    --runtime=python39 \
    --trigger-resource=sample-incoming-bucket \
    --trigger-event=google.storage.object.finalize \
    --entry-point=process_file
```

## Step 4: Verify Deployment
Check the function description:

```bash
gcloud functions describe process-transactions --region=us-central1
```
