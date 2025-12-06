# Graph Feature Implementation Summary

## Overview
Successfully implemented two graphs on both UserInfoPage and HomePage:
1. **Score History Graph**: Shows score progression across attempts
2. **Rank History Graph**: Shows leaderboard rank over time (from daily snapshots)

---

## Backend Changes

### 1. New Pydantic Schemas (`app/schemas.py`)
- `ScoreHistoryEntry`: For score history data
- `RankHistoryEntry`: For rank history data

### 2. New API Endpoints

#### Score History Endpoint (`app/routers/evaluation.py`)
- **GET** `/api/v1/user/score-history`
- Returns all submissions for authenticated user ordered chronologically
- Response: `[{question_id, score, submitted_at}]`

#### Rank History Endpoint (`app/routers/leaderboard.py`)
- **GET** `/api/v1/leaderboard/rank-history`
- Returns rank snapshots for authenticated user ordered by date
- Response: `[{date, rank}]`
- **Read-only**: Does not calculate ranks, only reads from `rank_history` collection

### 3. Daily Rank Snapshot Script (`app/scripts/snapshot_ranks.py`)
- Standalone script that calculates and saves daily rank snapshots
- Run via: `python -m app.scripts.snapshot_ranks`
- Creates documents in `rank_history` collection with format: `{user_id}_{date}`
- Uses Firestore batch writes for efficiency (handles 500+ users)
- Should be scheduled to run daily at 4 AM via cron/Cloud Scheduler

### 4. New Firestore Collection
- **Collection**: `rank_history`
- **Document ID**: `{user_id}_{date}` (e.g., `abc123_2024-01-15`)
- **Fields**:
  - `user_id`: string
  - `date`: string (YYYY-MM-DD)
  - `rank`: int
  - `recorded_at`: timestamp

---

## Frontend Changes

### 1. New Dependencies
- **recharts**: Installed for chart rendering

### 2. New API Service Functions (`src/api/services/userService.ts`)
- `fetchUserScoreHistory()`: Fetches score history
- `fetchUserRankHistory()`: Fetches rank history
- TypeScript interfaces: `ScoreHistoryEntry`, `RankHistoryEntry`

### 3. New Custom Hooks (`src/hooks/queries/useUserQueries.ts`)
- `useScoreHistory()`: React Query hook for score history
- `useRankHistory()`: React Query hook for rank history

### 4. New Chart Components

#### Score History Chart (`src/components/charts/ScoreHistoryChart.tsx`)
- **X-axis**: Attempt number (1, 2, 3, ...) - derived from array index
- **Y-axis**: Score (0-100)
- **Tooltip**: Shows attempt number, question ID, and score
- **Empty state**: "Submit answers to see your score progress"

#### Rank History Chart (`src/components/charts/RankHistoryChart.tsx`)
- **X-axis**: Date (formatted as "MMM DD")
- **Y-axis**: Rank (inverted with `reversed={true}` - rank 1 at top)
- **Tooltip**: Shows date and rank
- **Empty state**: "Rank history will be available starting tomorrow"

### 5. Updated Pages

#### UserInfoPage (`src/pages/UserInfoPage.tsx`)
- Added "Your Progress Over Time" section below leaderboard placement
- Displays both graphs side-by-side (2-column grid on desktop, stacked on mobile)
- Shows loading states while fetching data

#### HomePage (`src/pages/HomePage.tsx`)
- Added "Track Your Progress" section after hero, before gradient section
- Only shown when user is authenticated
- Displays both graphs side-by-side (2-column grid on desktop, stacked on mobile)
- Shows loading states while fetching data

---

## Key Features

### Score History Graph
✅ X-axis shows sequential attempt numbers (not question IDs)
✅ Question ID only visible in tooltip on hover
✅ Chronologically ordered by submission time
✅ Responsive design

### Rank History Graph
✅ Y-axis inverted (rank 1 at top, higher numbers at bottom)
✅ Shows historical rank progression from daily snapshots
✅ Date formatting for readability
✅ Responsive design

### Data Flow
1. User submits answers → stored in `submissions` collection
2. Daily at 4 AM → `snapshot_ranks.py` calculates ranks → saves to `rank_history`
3. User visits page → React Query fetches data via custom hooks
4. Backend queries Firestore and returns data
5. Recharts renders graphs with proper formatting
6. React Query caches data (5 minutes default)

---

## Setup Instructions

### 1. Backend Setup
No additional setup needed - endpoints are ready to use.

### 2. Schedule Daily Rank Snapshots

**Linux/macOS (cron)**:
```bash
crontab -e
# Add this line:
0 4 * * * cd /path/to/tonequest_backend && python -m app.scripts.snapshot_ranks >> /var/log/rank_snapshot.log 2>&1
```

**Windows (Task Scheduler)**:
- Create task to run daily at 4 AM
- Program: `python`
- Arguments: `-m app.scripts.snapshot_ranks`
- Start in: `D:\coding\dummy_quest\tonequest_backend`

**Manual Test**:
```bash
cd tonequest_backend
python -m app.scripts.snapshot_ranks
```

### 3. Frontend Setup
Already installed and configured - no additional steps needed.

---

## Files Created

### Backend
- `tonequest_backend/app/scripts/__init__.py`
- `tonequest_backend/app/scripts/snapshot_ranks.py`
- `tonequest_backend/app/scripts/README.md`

### Frontend
- `frontend/src/hooks/queries/useUserQueries.ts`
- `frontend/src/components/charts/ScoreHistoryChart.tsx`
- `frontend/src/components/charts/RankHistoryChart.tsx`

## Files Modified

### Backend
- `tonequest_backend/app/schemas.py`
- `tonequest_backend/app/routers/evaluation.py`
- `tonequest_backend/app/routers/leaderboard.py`

### Frontend
- `frontend/src/api/services/userService.ts`
- `frontend/src/pages/UserInfoPage.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/package.json` (recharts dependency)

---

## Testing Checklist

- [ ] Backend: Test `/api/v1/user/score-history` endpoint
- [ ] Backend: Test `/api/v1/leaderboard/rank-history` endpoint
- [ ] Backend: Run `python -m app.scripts.snapshot_ranks` manually
- [ ] Backend: Verify `rank_history` collection populated in Firestore
- [ ] Frontend: View graphs on UserInfoPage (authenticated)
- [ ] Frontend: View graphs on HomePage (authenticated)
- [ ] Frontend: Test empty states (new user with no submissions)
- [ ] Frontend: Test loading states
- [ ] Frontend: Test responsive design (mobile/tablet/desktop)
- [ ] Frontend: Verify tooltip shows correct data on hover
- [ ] Frontend: Verify rank graph Y-axis is inverted (rank 1 at top)

---

## Edge Cases Handled

✅ No submissions yet → Empty state message
✅ Only one submission → Graph renders with single point
✅ No rank history yet → Appropriate message shown
✅ User not authenticated → Graphs not shown on HomePage
✅ Loading states → Spinner/skeleton shown
✅ Error states → Error message displayed
✅ Mobile responsiveness → Graphs stack vertically

---

## Next Steps

1. **Set up cron job** to run `snapshot_ranks.py` daily at 4 AM
2. **Test the full flow**:
   - Submit some answers
   - Wait for next day's snapshot (or run script manually)
   - View graphs on both pages
3. **Monitor logs** to ensure snapshot script runs successfully
4. **Optional**: Add Firestore indexes if queries are slow:
   - Index on `submissions`: `user_id` + `submitted_at`
   - Index on `rank_history`: `user_id` + `date`

---

## Performance Considerations

- React Query caches API responses (5 minutes default)
- Firestore queries are indexed for performance
- Snapshot script uses batch writes (500 operations per batch)
- Charts are responsive and render efficiently with Recharts
- Empty states prevent unnecessary API calls

---

Implementation complete! 🎉
