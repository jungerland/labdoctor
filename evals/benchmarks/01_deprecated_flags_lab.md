# Building a Serverless Microservice on Cloud Run

In this lab, you will deploy a sample Python containerized service to Cloud Run.

## Step 1: Configure Environment Variables
Set your default project and region:
```bash
gcloud config set project demo-learning-proj
gcloud config set run/region us-central1
```

## Step 2: Store Service Secret
Create a secret to store database credentials:
```bash
gcloud secrets create api-token-secret --replication-policy=user-managed --data-file=/dev/null
```

## Step 3: Grant Secret Access
Grant default service account permission to read secret:
```bash
gcloud secrets add-iam-policy-binding api-token-secret --member="serviceAccount:demo@appspot.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
```

## Step 4: Deploy Container to Cloud Run
Deploy the microservice using gcloud CLI:
```bash
gcloud run deploy hello-service --image=gcr.io/cloudrun/hello --platform=managed --allow-unauthenticated
```
