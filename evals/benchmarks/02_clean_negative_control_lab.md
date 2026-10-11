# Modern Cloud Run Deployment with Secret Manager

In this lab, you will deploy a modern containerized workload to Google Cloud Run using current best practices.

## Step 1: Set Project Configuration
Initialize the active project and default deployment zone:
```bash
gcloud config set project demo-learning-proj
gcloud config set run/region us-central1
```

## Step 2: Provision Secret Manager Secret
Store application credentials securely without deprecated flags:
```bash
gcloud secrets create api-token-secret --data-file=/dev/null
```

## Step 3: Configure IAM Permissions
Grant the application runtime service account accessor privileges:
```bash
gcloud secrets add-iam-policy-binding api-token-secret --member="serviceAccount:demo@appspot.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
```

## Step 4: Deploy Cloud Run Service
Deploy the modern service using contemporary gcloud flags:
```bash
gcloud run deploy hello-service --image=gcr.io/cloudrun/hello --allow-unauthenticated
```
