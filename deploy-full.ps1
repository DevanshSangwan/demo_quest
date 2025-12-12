# Complete Firebase Deployment Script
# Run: .\deploy-full.ps1

$PROJECT_ID = "tonequest-79260"
$REGION = "us-central1"

Write-Host "🚀 Starting ToneQuest Deployment..." -ForegroundColor Green

# Step 1: Build & Push Docker Image
Write-Host "`n📦 Step 1: Building Docker image..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com containerregistry.googleapis.com

cd d:\coding\dummy_quest
docker build -t gcr.io/$PROJECT_ID/tonequest-backend:latest -f tonequest_backend/Dockerfile .

Write-Host "`n📤 Pushing to Container Registry..." -ForegroundColor Cyan
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/tonequest-backend:latest

# Step 2: Deploy to Cloud Run
Write-Host "`n☁️  Step 2: Deploying to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy tonequest-backend `
  --image gcr.io/$PROJECT_ID/tonequest-backend:latest `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS="http://localhost:5173" `
  --memory 512Mi `
  --timeout 300 `
  --max-instances 100

# Step 3: Get Cloud Run URL
Write-Host "`n🔗 Step 3: Getting Cloud Run URL..." -ForegroundColor Cyan
$CLOUD_RUN_URL = gcloud run services describe tonequest-backend --region $REGION --format='value(status.url)'
Write-Host "✅ Cloud Run URL: $CLOUD_RUN_URL" -ForegroundColor Green

# Step 4: Update Frontend Config
Write-Host "`n⚙️  Step 4: Updating frontend configuration..." -ForegroundColor Cyan
Write-Host "⚠️  MANUAL STEP: Update frontend/.env.production with:" -ForegroundColor Yellow
Write-Host "VITE_API_BASE_URL=$CLOUD_RUN_URL" -ForegroundColor Yellow
Read-Host "Press Enter after updating .env.production"

# Step 5: Build Frontend
Write-Host "`n🏗️  Step 5: Building frontend..." -ForegroundColor Cyan
cd d:\coding\dummy_quest\frontend
npm install
npm run build

# Step 6: Deploy Frontend
Write-Host "`n🔥 Step 6: Deploying to Firebase Hosting..." -ForegroundColor Cyan
cd d:\coding\dummy_quest
firebase deploy --only hosting

# Step 7: Deploy Firestore Rules
Write-Host "`n📋 Step 7: Deploying Firestore rules..." -ForegroundColor Cyan
firebase deploy --only firestore:rules

Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to Firebase Console > Firestore Database"
Write-Host "2. Create collection 'QnA' and add sample documents"
Write-Host "3. Test the application at: https://tonequest-79260.web.app"
Write-Host "4. Check backend health: $CLOUD_RUN_URL/api/v1/health"
