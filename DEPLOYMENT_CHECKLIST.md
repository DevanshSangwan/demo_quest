# Firebase Deployment Checklist

## Pre-Deployment ✓

- [ ] Google Cloud Account created with billing enabled
- [ ] Firebase Project created
- [ ] gcloud CLI installed and authenticated
- [ ] Docker installed
- [ ] Firebase CLI installed (`npm install -g firebase-tools`)
- [ ] Firebase credentials downloaded as `tonequest_backend/app/ServiceAccountKey.json`

## Backend Deployment

- [ ] Dockerfile created in `tonequest_backend/`
- [ ] Backend updated with environment variable CORS configuration
- [ ] Docker image built: `docker build -t gcr.io/$PROJECT_ID/tonequest-backend:latest -f tonequest_backend/Dockerfile .`
- [ ] Docker image pushed to Container Registry
- [ ] Cloud Run service deployed with correct environment variables
- [ ] Cloud Run URL obtained and noted

## Frontend Deployment

- [ ] `frontend/.env.production` updated with Cloud Run URL
- [ ] Firebase configuration values added to `.env.production`
- [ ] Frontend built: `npm run build`
- [ ] `dist/` folder created successfully
- [ ] Frontend deployed to Firebase Hosting: `firebase deploy --only hosting`
- [ ] Firebase Hosting URL obtained and noted

## Firestore Setup

- [ ] Firestore security rules deployed: `firebase deploy --only firestore:rules`
- [ ] Firestore indexes deployed: `firebase deploy --only firestore`
- [ ] Sample QnA collection created with test data
- [ ] Security rules tested and verified

## Post-Deployment Verification

- [ ] Backend health check: `curl https://YOUR_CLOUD_RUN_URL/api/v1/health`
- [ ] Frontend loads at Firebase Hosting URL
- [ ] Authentication works (sign up/login)
- [ ] Questions load correctly
- [ ] Evaluation endpoint responds
- [ ] Leaderboard displays data
- [ ] No CORS errors in browser console

## Monitoring & Maintenance

- [ ] Cloud Run logs accessible: `gcloud run logs read tonequest-backend`
- [ ] Firebase Hosting logs accessible: `firebase hosting:log`
- [ ] Budget alerts configured in GCP Console
- [ ] Error tracking setup (optional: Sentry, Cloud Logging)
- [ ] Performance monitoring enabled

## Security

- [ ] ServiceAccountKey.json in .gitignore
- [ ] Environment variables not committed to Git
- [ ] Firestore security rules restrict unauthorized access
- [ ] CORS origins limited to Firebase Hosting URL
- [ ] Firebase Authentication enabled
- [ ] Cloud Run service not publicly accessible (if needed)

## Troubleshooting

### If CORS errors occur:
```bash
gcloud run deploy tonequest-backend \
  --update-env-vars ALLOWED_ORIGINS=https://your-firebase-hosting-url.web.app \
  --region us-central1
```

### If authentication fails:
- Verify ServiceAccountKey.json location
- Check Firebase project ID in frontend `.env.production`
- Verify Firestore is enabled in Firebase Console

### If questions don't load:
- Check QnA collection exists in Firestore
- Verify Firestore security rules allow reads
- Check backend logs for errors

### If API calls fail:
- Verify VITE_API_BASE_URL in frontend `.env.production`
- Check Cloud Run service is running
- Verify backend health: `curl https://YOUR_CLOUD_RUN_URL/api/v1/health`

## Useful Commands

```bash
# View Cloud Run services
gcloud run services list

# View Cloud Run logs
gcloud run logs read tonequest-backend --region us-central1 --limit=50

# Update Cloud Run environment variables
gcloud run deploy tonequest-backend --update-env-vars KEY=VALUE --region us-central1

# View Firebase Hosting deployments
firebase hosting:channel:list

# View Firestore data
firebase firestore:get /QnA

# Deploy only specific components
firebase deploy --only hosting
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes
```

## Cost Estimates (Monthly)

- **Cloud Run**: ~$0.40 per million requests (first 2M free)
- **Firebase Hosting**: 10GB free storage, 360M free bandwidth
- **Firestore**: 50k free reads/day, 20k free writes/day
- **Total**: Likely free tier for small projects

## Next Steps

1. Monitor application performance
2. Set up error alerts
3. Configure custom domain (optional)
4. Implement rate limiting
5. Enable Cloud Armor for DDoS protection
6. Set up CI/CD pipeline for automated deployments

