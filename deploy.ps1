# ToneQuest Firebase Deployment Script
# Run this script to deploy to Firebase

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1"
)

if (-not $ProjectId) {
    Write-Host "Usage: .\deploy.ps1 -ProjectId <your-gcp-project-id>"
    exit 1
}

Write-Host "🚀 Starting ToneQuest Deployment..." -ForegroundColor Green

# Step 1: Set GCP Project
Write-Host "`n📋 Setting GCP Project..." -ForegroundColor Cyan
gcloud config set project $ProjectId

# Step 2: Enable APIs
Write-Host "`n🔧 Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Step 3: Build Docker Image
Write-Host "`n🐳 Building Docker image..." -ForegroundColor Cyan
docker build -t gcr.io/$ProjectId/tonequest-backend:latest -f tonequest_backend/Dockerfile .

# Step 4: Push to Container Registry
Write-Host "`n📤 Pushing image to Container Registry..." -ForegroundColor Cyan
gcloud auth configure-docker
docker push gcr.io/$ProjectId/tonequest-backend:latest

# Step 5: Deploy to Cloud Run
Write-Host "`n☁️  Deploying to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy tonequest-backend `
  --image gcr.io/$ProjectId/tonequest-backend:latest `
  --platform managed `
  --region $Region `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS="http://localhost:5173" `
  --memory 512Mi `
  --timeout 300

# Get Cloud Run URL
$CLOUD_RUN_URL = gcloud run services describe tonequest-backend --region $Region --format='value(status.url)'
Write-Host "`n✅ Cloud Run URL: $CLOUD_RUN_URL" -ForegroundColor Green

# Step 6: Build Frontend
Write-Host "`n🏗️  Building frontend..." -ForegroundColor Cyan
cd frontend
npm install
npm run build
cd ..

# Step 7: Deploy to Firebase Hosting
Write-Host "`n🔥 Deploying to Firebase Hosting..." -ForegroundColor Cyan
firebase deploy --only hosting

Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update frontend/.env.production with Cloud Run URL: $CLOUD_RUN_URL"
Write-Host "2. Rebuild frontend: cd frontend && npm run build"
Write-Host "3. Redeploy frontend: firebase deploy --only hosting"
Write-Host "4. Deploy Firestore rules: firebase deploy --only firestore:rules"
