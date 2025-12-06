#!/usr/bin/env python3
"""
Daily rank snapshot script.
Run this script daily at 4 AM via cron or Cloud Scheduler.

Usage:
    python -m app.scripts.snapshot_ranks
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.cloud import firestore
from app.firebase_config import db


def snapshot_daily_ranks():
    """
    Calculate current leaderboard rankings and save a snapshot for each user.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    print(f"Starting rank snapshot for {today}...")
    
    try:
        # Fetch all leaderboard entries ordered by average_score descending
        query = (
            db.collection("leaderboard")
            .order_by("average_score", direction=firestore.Query.DESCENDING)
        )
        documents = list(query.stream())
        
        if not documents:
            print("No leaderboard entries found. Exiting.")
            return
        
        print(f"Found {len(documents)} users on leaderboard.")
        
        # Calculate ranks and save snapshots
        rank_history_ref = db.collection("rank_history")
        batch = db.batch()
        batch_count = 0
        
        for rank, doc in enumerate(documents, start=1):
            data = doc.to_dict() or {}
            user_id = data.get("user_id", doc.id)
            
            # Create document ID: {user_id}_{date}
            doc_id = f"{user_id}_{today}"
            snapshot_ref = rank_history_ref.document(doc_id)
            
            snapshot_data = {
                "user_id": user_id,
                "date": today,
                "rank": rank,
                "recorded_at": datetime.now(timezone.utc),
            }
            
            batch.set(snapshot_ref, snapshot_data)
            batch_count += 1
            
            # Firestore batch limit is 500 operations
            if batch_count >= 500:
                batch.commit()
                print(f"Committed batch of {batch_count} snapshots.")
                batch = db.batch()
                batch_count = 0
        
        # Commit remaining snapshots
        if batch_count > 0:
            batch.commit()
            print(f"Committed final batch of {batch_count} snapshots.")
        
        print(f"✓ Successfully created rank snapshots for {len(documents)} users.")
        
    except Exception as exc:
        print(f"✗ Error creating rank snapshots: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    snapshot_daily_ranks()
