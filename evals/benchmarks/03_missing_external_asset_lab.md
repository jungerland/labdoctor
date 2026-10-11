# Ingesting Financial Datasets from Cloud Storage

Learn how to pull raw financial transaction datasets from Google Cloud Storage.

## Step 1: Set Project Configuration
```bash
gcloud config set project demo-learning-proj
```

## Step 2: Download Historical Sample Dataset
Download the sample dataset from historical training storage:
```bash
gsutil cp gs://expired-legacy-training-bucket-2022/sample_transactions.csv ./data/
```
