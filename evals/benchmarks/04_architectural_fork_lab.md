# Cloud Storage Event-Driven Processing

Trigger asynchronous worker processes on Cloud Storage file uploads.

## Step 1: Set Project Configuration
```bash
gcloud config set project demo-learning-proj
```

## Step 2: Deploy Cloud Function Background Trigger
Deploy legacy 1st gen background trigger function:
```bash
gcloud functions deploy thumbnail-processor --runtime=python39 --trigger-resource=my-input-bucket --trigger-event=google.storage.object.finalize
```
