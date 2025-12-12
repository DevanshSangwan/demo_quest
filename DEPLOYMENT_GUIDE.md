# Firebase Deployment Guide for ToneQuest

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Firebase Project** created
3. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
4. **Docker** installed: https://docs.docker.com/get-docker/
5. **Firebase CLI** installed: `npm install -g firebase-tools`

---

## Step 1: Setup GCP Project

```bash
# Set your project ID
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"

# Set default project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## Step 2: Prepare Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to **Project Settings > Service Accounts**
4. Click **Generate New Private Key**
5. Save as `tonequest_backend/app/ServiceAccountKey.json`

**Important**: Never commit this file to Git!

---

## Step 3: Build and Push Docker Image

```bash
# Navigate to project root
cd d:\coding\dummy_quest

# Build Docker image
docker build -t gcr.io/$PROJECT_ID/tonequest-backend:latest -f tonequest_backend/Dockerfile .

# Configure Docker authentication
gcloud auth configure-docker

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/tonequest-backend:latest
```

---

## Step 4: Deploy Backend to Cloud Run

```bash
# Get your Firebase Hosting URL (you'll set this after frontend deployment)
$FIREBASE_HOSTING_URL = "https://your-project.web.app"

# Deploy to Cloud Run
gcloud run deploy tonequest-backend `
  --image gcr.io/$PROJECT_ID/tonequest-backend:latest `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS=$FIREBASE_HOSTING_URL `
  --memory 512Mi `
  --timeout 300 `
  --max-instances 100

# Get Cloud Run URL
$CLOUD_RUN_URL = gcloud run services describe tonequest-backend --region $REGION --format='value(status.url)'
Write-Host "Cloud Run URL: $CLOUD_RUN_URL"
```

---

## Step 5: Update Frontend Configuration

1. Open `frontend/.env.production`
2. Replace `YOUR_CLOUD_RUN_URL` with the URL from Step 4
3. Update Firebase configuration values from Firebase Console

```bash
# Example
VITE_API_BASE_URL=https://tonequest-backend-xxxxx.run.app
```

---

## Step 6: Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Verify dist folder is created
ls dist
```

---

## Step 7: Deploy Frontend to Firebase Hosting

```bash
# From project root
firebase login

# Initialize Firebase (if not done)
firebase init hosting

# Deploy
firebase deploy --only hosting
```

Get your Firebase Hosting URL from the deployment output.

---

## Step 8: Update Cloud Run with Firebase Hosting URL

```bash
# Update CORS with Firebase Hosting URL
$FIREBASE_URL = "https://your-project.web.app"

gcloud run deploy tonequest-backend `
  --update-env-vars ALLOWED_ORIGINS=$FIREBASE_URL `
  --region $REGION
```

---

## Step 9: Deploy Firestore Rules

```bash
# From project root
firebase deploy --only firestore:rules
```

---

## Step 10: Seed Firestore Data

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project > Firestore Database
3. Create collection `QnA`
4. Add sample documents:

```json
{
  "id": 1,
  "prompt_text": "Describe a time when you had to handle a difficult client situation.",
  "category": "Professional Communication",
  "difficulty": "Medium",
  "answers": [
    "I once worked with a client who was unhappy with our initial deliverable...",
    "When faced with a challenging client, I prioritize active listening..."
  ]
}
```

---

## Verification

### Test Backend
```bash
curl https://YOUR_CLOUD_RUN_URL/api/v1/health
```

### Test Frontend
Visit: `https://your-project.web.app`

### View Logs
```bash
# Cloud Run logs
gcloud run logs read tonequest-backend --region $REGION --limit=50

# Firebase Hosting logs
firebase hosting:log
```

---

## Troubleshooting

### CORS Errors
- Verify `ALLOWED_ORIGINS` environment variable in Cloud Run
- Check Firebase Hosting URL matches exactly

### Authentication Fails
- Verify `ServiceAccountKey.json` is in correct location
- Check Firebase project ID matches in frontend `.env.production`

### Questions Not Loading
- Verify `QnA` collection exists in Firestore
- Check Firestore security rules allow reads

### API Calls Fail
- Verify `VITE_API_BASE_URL` in frontend `.env.production`
- Check Cloud Run service is running: `gcloud run services list`

---

## Cost Optimization

- Cloud Run: Pay only for requests (~$0.40 per million requests)
- Firebase Hosting: 10GB free storage, 360M free bandwidth/month
- Firestore: 50k free reads/day, 20k free writes/day
- Set up budget alerts in GCP Console

---

## Monitoring

### Setup Cloud Run Monitoring
```bash
gcloud monitoring dashboards create --config-from-file=- <<EOF
{
  "displayName": "ToneQuest Backend",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Count",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"tonequest-backend\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF
```

---

## Next Steps

1. Monitor logs and performance
2. Set up error alerts
3. Configure custom domain (optional)
4. Implement rate limiting
5. Enable Cloud Armor for DDoS protection

