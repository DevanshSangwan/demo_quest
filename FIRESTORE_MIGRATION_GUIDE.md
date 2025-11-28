# Firestore Migration Guide: SentenceTransformer → Gemini API

## Overview

After switching from SentenceTransformer-based evaluation to Gemini API, the Firestore schema has changed. This guide documents the changes and provides migration steps.

---

## 📊 Schema Changes

### 1. **submissions** Collection

#### ❌ OLD FIELDS (Removed)
```javascript
{
  "similarity_score": 0.87,        // Cosine similarity (0-1)
  "best_match_answer": "I led..."  // Reference answer that matched best
}
```

#### ✅ NEW FIELDS (Added)
```javascript
{
  "score": 85,                     // Gemini score (0-100)
  "tone_feedback": "Professional and confident...",
  "grammar_issues": ["Consider varying sentence length"],
  "suggestions": "Add concrete examples...",
  "llm_feedback": {                // Full Gemini response
    "score": 85,
    "toneFeedback": "...",
    "grammarIssues": [...],
    "suggestions": "..."
  }
}
```

#### 📝 COMPLETE NEW SCHEMA
```javascript
{
  "user_id": "firebase_uid",
  "question_id": "1",
  "submitted_answer": "User's answer text...",
  "score": 85,                     // NEW: 0-100 instead of 0-1
  "tone_feedback": "...",          // NEW
  "grammar_issues": [...],         // NEW
  "suggestions": "...",            // NEW
  "llm_feedback": {...},           // NEW
  "submitted_at": Timestamp
}
```

### 2. **leaderboard** Collection

#### ✅ NO CHANGES NEEDED
The leaderboard collection remains the same because it stores aggregated scores:

```javascript
{
  "user_id": "firebase_uid",
  "total_score": 425.5,
  "submission_count": 5,
  "average_score": 85.1,
  "best_score": 92.0,
  "updated_at": Timestamp
}
```

**Note:** Scores are now 0-100 instead of 0-1, but the structure is identical.

### 3. **QnA** Collection

#### ⚠️ FIELD REMOVED: `answers`
The `answers` field (reference answers) is no longer needed since Gemini evaluates without comparing to reference answers.

**New Schema:**
```javascript
{
  "id": 1,
  "question_text": "Describe a time...",
  "category": "Professional Communication",  // Optional
  "difficulty": "Medium"                     // Optional
}
```

**Note:** Existing `answers` fields in Firestore can remain (they're simply ignored), or you can remove them manually if desired.

### 4. **users** Collection

#### ✅ NO CHANGES NEEDED
User documents remain the same:

```javascript
{
  "uid": "firebase_uid",
  "email": "user@example.com",
  "displayName": "John Doe",
  "totalSubmissions": 5,
  "answeredQuestionIds": [1, 2, 3]
}
```

---

## 🔄 Migration Required?

### ✅ **NO MIGRATION NEEDED** if:
- You're starting fresh
- You don't have existing submissions
- You're okay with old submissions having different schema

### ⚠️ **MIGRATION RECOMMENDED** if:
- You have existing submissions in production
- You need consistent schema across all submissions
- You want to display old submissions with new fields

---

## 🛠️ Migration Options

### Option 1: **No Migration (Recommended for Development)**

**Pros:**
- No work required
- Old data still readable
- New submissions use new schema

**Cons:**
- Inconsistent schema
- Old submissions missing new fields

**When to use:** Development, testing, or if you have minimal existing data

### Option 2: **Soft Migration (Add Default Values)**

Update your code to handle both old and new schemas:

```python
# In your frontend/backend when reading submissions:
submission = doc.to_dict()

# Handle old schema
if "similarity_score" in submission:
    # Old submission - convert to new format
    score = submission.get("similarity_score", 0) * 100  # Convert 0-1 to 0-100
    tone_feedback = "Legacy submission - no feedback available"
    grammar_issues = []
    suggestions = "Legacy submission - no suggestions available"
else:
    # New submission
    score = submission.get("score", 0)
    tone_feedback = submission.get("tone_feedback", "")
    grammar_issues = submission.get("grammar_issues", [])
    suggestions = submission.get("suggestions", "")
```

### Option 3: **Hard Migration (Update All Documents)**

Run a migration script to update all existing submissions:

```python
# migration_script.py
from google.cloud import firestore
from app.firebase_config import db

def migrate_submissions():
    """
    Migrate old submissions to new schema.
    """
    submissions_ref = db.collection("submissions")
    docs = submissions_ref.stream()
    
    migrated_count = 0
    skipped_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        
        # Check if already migrated
        if "score" in data and "tone_feedback" in data:
            skipped_count += 1
            continue
        
        # Migrate old schema to new
        updates = {}
        
        # Convert similarity_score (0-1) to score (0-100)
        if "similarity_score" in data:
            updates["score"] = data["similarity_score"] * 100
        else:
            updates["score"] = 0
        
        # Add new fields with default values
        updates["tone_feedback"] = "Legacy submission - migrated from old system"
        updates["grammar_issues"] = []
        updates["suggestions"] = "No suggestions available for legacy submissions"
        updates["llm_feedback"] = {
            "score": updates["score"],
            "toneFeedback": updates["tone_feedback"],
            "grammarIssues": [],
            "suggestions": updates["suggestions"]
        }
        
        # Update document
        doc.reference.update(updates)
        migrated_count += 1
        
        print(f"Migrated: {doc.id}")
    
    print(f"\nMigration complete!")
    print(f"Migrated: {migrated_count}")
    print(f"Skipped: {skipped_count}")

if __name__ == "__main__":
    migrate_submissions()
```

**To run:**
```bash
cd tonequest_backend
python migration_script.py
```

---

## 📋 Migration Checklist

### Before Migration
- [ ] Backup Firestore data (export to Cloud Storage)
- [ ] Test migration script on a copy of data
- [ ] Verify new code works with both old and new schemas

### During Migration
- [ ] Run migration script
- [ ] Monitor for errors
- [ ] Verify sample documents updated correctly

### After Migration
- [ ] Test application end-to-end
- [ ] Verify leaderboard calculations still work
- [ ] Check that old submissions display correctly
- [ ] Remove old field handling code (optional)

---

## 🔍 Verification Queries

### Check for Old Schema Documents
```javascript
// In Firestore Console
db.collection("submissions")
  .where("similarity_score", "!=", null)
  .get()
```

### Check for New Schema Documents
```javascript
db.collection("submissions")
  .where("tone_feedback", "!=", null)
  .get()
```

### Verify Leaderboard Scores
```javascript
db.collection("leaderboard")
  .orderBy("average_score", "desc")
  .limit(10)
  .get()
```

---

## ⚠️ Important Notes

### Score Scale Change
- **Old:** 0.0 to 1.0 (similarity score)
- **New:** 0 to 100 (Gemini score)

**Impact on Leaderboard:**
- If you have old submissions with scores like 0.85, they'll be much lower than new scores like 85
- **Solution:** Multiply old scores by 100 during migration

### Backward Compatibility
The current code is **backward compatible** for reading:
- Old submissions can still be read (missing fields will be `None`)
- New submissions use the new schema
- Leaderboard aggregation works with both

### Forward Compatibility
New code **cannot write** old schema:
- All new submissions will use Gemini schema
- No way to create old-style submissions anymore

---

## 🎯 Recommended Approach

### For Development/Testing:
**Use Option 1 (No Migration)**
- Just start using the new system
- Old data can coexist with new data

### For Production with Existing Data:
**Use Option 2 (Soft Migration)**
- Add code to handle both schemas
- Gradually phase out old data
- No downtime required

### For Clean Production Deployment:
**Use Option 3 (Hard Migration)**
- Run migration script during maintenance window
- All data uses consistent schema
- Cleaner codebase

---

## 📞 Support

If you encounter issues during migration:
1. Check Firestore console for document structure
2. Verify migration script ran successfully
3. Test with a single document first
4. Keep backups until migration is verified

---

## Summary

**Good News:** Most collections don't need changes! Only the `submissions` collection has schema changes, and the current code is backward compatible for reading.

**Action Required:** 
- ✅ None for development
- ⚠️ Consider migration for production with existing data
- 🔄 Run migration script if you want consistent schema
