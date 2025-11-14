# Firestore Configuration for Question Serving Flow

## Collections Structure

### 1. `QnA` Collection (Questions)

Each question document MUST have the following structure:

```json
{
  "id": 1,  // REQUIRED: Sequential integer (1, 2, 3, ...)
  "question_text": "Your question text here",
  "answers": [
    "Reference answer 1",
    "Reference answer 2",
    "Reference answer 3"
  ]
}
```

**CRITICAL Requirements:**
- The `id` field MUST be a sequential integer starting from 1
- Questions will be served in order: 1, 2, 3, ..., N
- The document ID in Firestore can be anything, but the `id` field inside the document is what matters

**Example Questions:**

Document ID: `question_001`
```json
{
  "id": 1,
  "question_text": "Describe a professional accomplishment you are particularly proud of.",
  "answers": [
    "I led a cross-functional team that delivered a critical project ahead of schedule.",
    "I launched a new onboarding program that reduced ramp-up time by 30%."
  ]
}
```

Document ID: `question_002`
```json
{
  "id": 2,
  "question_text": "Tell me about a time you faced a significant challenge at work.",
  "answers": [
    "I resolved a critical production issue by coordinating with multiple teams.",
    "I managed conflicting priorities by establishing clear communication channels."
  ]
}
```

### 2. `users` Collection

Each user document now includes:

```json
{
  "uid": "firebase_user_id",
  "email": "user@example.com",
  "displayName": "User Name",
  "totalSubmissions": 0,
  "answeredQuestionIds": []  // NEW: Tracks which questions user has answered
}
```

The `answeredQuestionIds` array will automatically populate as users answer questions.

### 3. `submissions` Collection (Unchanged)

Stores user answer submissions with evaluation scores.

### 4. `leaderboard` Collection (Unchanged)

Stores aggregated user performance metrics.

## How the Flow Works

1. **User starts answering**: Backend checks `answeredQuestionIds` in user profile
2. **Serve next question**: Backend finds the smallest question `id` NOT in `answeredQuestionIds`
3. **User submits answer**: Backend evaluates and adds question `id` to `answeredQuestionIds`
4. **Completion**: When all question IDs are in `answeredQuestionIds`, show completion message

## Migration for Existing Users

Existing users without the `answeredQuestionIds` field will work fine - the backend handles missing fields gracefully. They'll start from question 1, and the field will be created on their first answer submission.

### Option 1: Do Nothing (Recommended)
The field will be automatically created when users submit their first answer.

### Option 2: Manual Update (Few Users)
1. Go to Firebase Console → Firestore → `users` collection
2. For each user document, add field:
   - Name: `answeredQuestionIds`
   - Type: `array`
   - Value: empty array

### Option 3: Migration Script (Many Users)
Run the migration script:
```bash
cd tonequest_backend
python migrate_users.py
```
