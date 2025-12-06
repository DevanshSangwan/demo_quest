# Rank Snapshot Script

## Overview

The `snapshot_ranks.py` script creates daily snapshots of user rankings on the leaderboard. This enables the rank history graph feature in the frontend.

## How It Works

1. Fetches all users from the `leaderboard` collection
2. Orders them by `average_score` (descending)
3. Calculates rank for each user (1, 2, 3, ...)
4. Saves a snapshot to the `rank_history` collection with format: `{user_id}_{date}`

## Manual Execution

From the `tonequest_backend` directory:

```bash
python -m app.scripts.snapshot_ranks
```

## Automated Scheduling

### Option 1: Linux/macOS Cron

Edit your crontab:
```bash
crontab -e
```

Add this line to run daily at 4 AM:
```bash
0 4 * * * cd /path/to/tonequest_backend && /path/to/python -m app.scripts.snapshot_ranks >> /var/log/rank_snapshot.log 2>&1
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 4:00 AM
4. Set action: Start a program
   - Program: `python`
   - Arguments: `-m app.scripts.snapshot_ranks`
   - Start in: `D:\coding\dummy_quest\tonequest_backend`

### Option 3: Google Cloud Scheduler (for GCP deployments)

```bash
gcloud scheduler jobs create http rank-snapshot \
  --schedule="0 4 * * *" \
  --uri="https://your-cloud-run-url/api/v1/admin/snapshot-ranks" \
  --http-method=POST \
  --oidc-service-account-email=your-service-account@project.iam.gserviceaccount.com
```

## Firestore Structure

Each snapshot creates a document in the `rank_history` collection:

```json
{
  "user_id": "abc123",
  "date": "2024-01-15",
  "rank": 5,
  "recorded_at": "2024-01-15T04:00:00Z"
}
```

Document ID format: `{user_id}_{date}` (e.g., `abc123_2024-01-15`)

## Troubleshooting

- **No output**: Check that Firebase credentials are properly configured
- **Permission errors**: Ensure the service account has Firestore write permissions
- **Missing data**: Verify the `leaderboard` collection has entries
