"""
Firestore Migration Script: SentenceTransformer → Gemini API

This script migrates old submission documents to the new Gemini-based schema.

Usage:
    python migrate_firestore.py [--dry-run] [--confirm]

Options:
    --dry-run    Show what would be migrated without making changes
    --confirm    Skip confirmation prompt (use with caution)
"""

import sys
from google.cloud import firestore
from app.firebase_config import db


def migrate_submissions(dry_run=False):
    """
    Migrate old submissions to new Gemini-based schema.
    
    Old schema:
        - similarity_score (0-1)
        - best_match_answer (string)
    
    New schema:
        - score (0-100)
        - tone_feedback (string)
        - grammar_issues (array)
        - suggestions (string)
        - llm_feedback (object)
    """
    print("=" * 60)
    print("Firestore Migration: SentenceTransformer -> Gemini API")
    print("=" * 60)
    
    if dry_run:
        print("\n[DRY RUN] No changes will be made\n")
    else:
        print("\n[LIVE MODE] Documents will be updated\n")
        if "--confirm" not in sys.argv:
            response = input("Continue? (yes/no): ")
            if response.lower() != "yes":
                print("Migration cancelled.")
                return
        else:
            print("[AUTO-CONFIRMED] Proceeding with migration...\n")
    
    submissions_ref = db.collection("submissions")
    
    try:
        docs = list(submissions_ref.stream())
        total_docs = len(docs)
        print(f"\nFound {total_docs} submission documents\n")
    except Exception as e:
        print(f"❌ Error fetching submissions: {e}")
        return
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, doc in enumerate(docs, 1):
        doc_id = doc.id
        data = doc.to_dict() or {}
        
        print(f"[{idx}/{total_docs}] Processing: {doc_id}")
        
        # Check if already migrated (has new schema fields)
        if "tone_feedback" in data and "grammar_issues" in data:
            print(f"  [OK] Already migrated - skipping")
            skipped_count += 1
            continue
        
        # Check if it's an old schema document
        has_old_schema = "similarity_score" in data or "best_match_answer" in data
        
        if not has_old_schema:
            # Document has neither old nor new schema - might be corrupted
            print(f"  [WARN] Unknown schema - skipping")
            skipped_count += 1
            continue
        
        # Prepare migration updates
        updates = {}
        
        # Convert similarity_score (0-1) to score (0-100)
        if "similarity_score" in data:
            old_score = float(data.get("similarity_score", 0))
            new_score = round(old_score * 100, 2)
            updates["score"] = new_score
            print(f"  [SCORE] Converting: {old_score} -> {new_score}")
        else:
            updates["score"] = 0.0
            print(f"  [SCORE] No old score found, setting to 0")
        
        # Add new Gemini fields with default values
        updates["tone_feedback"] = "Legacy submission - migrated from similarity-based evaluation"
        updates["grammar_issues"] = []
        updates["suggestions"] = "This submission was evaluated using the old system. No detailed feedback available."
        
        # Create llm_feedback object
        updates["llm_feedback"] = {
            "score": updates["score"],
            "toneFeedback": updates["tone_feedback"],
            "grammarIssues": updates["grammar_issues"],
            "suggestions": updates["suggestions"]
        }
        
        # Optionally remove old fields (commented out to preserve data)
        # updates["similarity_score"] = firestore.DELETE_FIELD
        # updates["best_match_answer"] = firestore.DELETE_FIELD
        
        if dry_run:
            print(f"  [DRY-RUN] Would update with: {list(updates.keys())}")
            migrated_count += 1
        else:
            try:
                doc.reference.update(updates)
                print(f"  [SUCCESS] Migrated successfully")
                migrated_count += 1
            except Exception as e:
                print(f"  [ERROR] Error updating: {e}")
                error_count += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Total documents:     {total_docs}")
    print(f"[OK] Migrated:       {migrated_count}")
    print(f"[SKIP] Skipped:      {skipped_count}")
    print(f"[ERROR] Errors:      {error_count}")
    print("=" * 60)
    
    if dry_run:
        print("\n[INFO] Run without --dry-run to apply changes")
    else:
        print("\n[SUCCESS] Migration complete!")


def verify_migration():
    """
    Verify that migration was successful by checking document schemas.
    """
    print("\n" + "=" * 60)
    print("Verifying Migration")
    print("=" * 60)
    
    submissions_ref = db.collection("submissions")
    
    try:
        docs = list(submissions_ref.stream())
        total = len(docs)
        
        old_schema = 0
        new_schema = 0
        mixed_schema = 0
        
        for doc in docs:
            data = doc.to_dict() or {}
            
            has_old = "similarity_score" in data or "best_match_answer" in data
            has_new = "tone_feedback" in data and "grammar_issues" in data
            
            if has_old and has_new:
                mixed_schema += 1
            elif has_new:
                new_schema += 1
            elif has_old:
                old_schema += 1
        
        print(f"\nTotal documents:     {total}")
        print(f"[OK] New schema:     {new_schema}")
        print(f"[WARN] Mixed schema: {mixed_schema}")
        print(f"[OLD] Old schema:    {old_schema}")
        
        if old_schema == 0:
            print("\n[SUCCESS] All documents migrated successfully!")
        else:
            print(f"\n[WARN] {old_schema} documents still need migration")
        
    except Exception as e:
        print(f"[ERROR] Error during verification: {e}")


if __name__ == "__main__":
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    # Run migration
    migrate_submissions(dry_run=dry_run)
    
    # Verify if not dry-run
    if not dry_run:
        verify_migration()
