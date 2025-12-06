# Quick Testing Guide for Graph Features

## Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- User account created and logged in

---

## Step 1: Test Score History Graph

### Generate Test Data
1. Log in to the application
2. Navigate to the Answering page
3. Submit 3-5 answers to different questions
4. Each submission creates an entry in the `submissions` collection

### View Score History
1. Navigate to **User Info Page** (`/user`)
2. Scroll to "Your Progress Over Time" section
3. You should see the **Score Progress** graph with:
   - X-axis: Attempt numbers (1, 2, 3, ...)
   - Y-axis: Scores (0-100)
   - Hover over points to see question ID in tooltip

4. Navigate to **Home Page** (`/`)
5. Scroll to "Track Your Progress" section (below hero)
6. Same graph should appear

### Expected Behavior
- ✅ Graph shows all your submissions in chronological order
- ✅ X-axis shows sequential attempt numbers
- ✅ Tooltip shows: Attempt #, Question ID, Score
- ✅ Line connects all data points
- ✅ Graph is responsive (try resizing browser)

---

## Step 2: Test Rank History Graph

### Generate Rank Snapshots

**Option A: Manual Script Execution (Recommended for Testing)**
```bash
cd tonequest_backend
python -m app.scripts.snapshot_ranks
```

Expected output:
```
Starting rank snapshot for 2024-01-15...
Found X users on leaderboard.
Committed final batch of X snapshots.
✓ Successfully created rank snapshots for X users.
```

**Option B: Wait for Scheduled Run**
- If you've set up the cron job, wait until 4 AM next day
- Not recommended for immediate testing

### Verify Firestore Data
1. Open Firebase Console
2. Go to Firestore Database
3. Check `rank_history` collection
4. You should see documents with IDs like: `{your_user_id}_2024-01-15`
5. Each document should have: `user_id`, `date`, `rank`, `recorded_at`

### View Rank History
1. Navigate to **User Info Page** (`/user`)
2. Scroll to "Your Progress Over Time" section
3. You should see the **Rank History** graph with:
   - X-axis: Dates (formatted as "Jan 15", "Jan 16", etc.)
   - Y-axis: Rank (inverted - rank 1 at top)
   - Hover over points to see exact date and rank

4. Navigate to **Home Page** (`/`)
5. Scroll to "Track Your Progress" section
6. Same graph should appear

### Expected Behavior
- ✅ Graph shows rank progression over time
- ✅ Y-axis is inverted (rank 1 at top, higher numbers at bottom)
- ✅ Tooltip shows: Date and Rank
- ✅ Line connects all data points
- ✅ Graph is responsive

---

## Step 3: Test Empty States

### New User (No Submissions)
1. Create a new user account
2. Log in
3. Navigate to User Info Page or Home Page
4. Expected messages:
   - Score graph: "Submit answers to see your score progress"
   - Rank graph: "Rank history will be available starting tomorrow..."

### User with Submissions but No Rank History
1. Submit answers but don't run snapshot script
2. Expected:
   - Score graph: Shows data
   - Rank graph: Shows empty state message

---

## Step 4: Test API Endpoints Directly

### Score History Endpoint
```bash
# Get your auth token from browser DevTools (Application > Local Storage)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/user/score-history
```

Expected response:
```json
[
  {
    "question_id": 1,
    "score": 75.5,
    "submitted_at": "2024-01-15T10:30:00"
  },
  {
    "question_id": 2,
    "score": 82.0,
    "submitted_at": "2024-01-15T11:45:00"
  }
]
```

### Rank History Endpoint
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/leaderboard/rank-history
```

Expected response:
```json
[
  {
    "date": "2024-01-15",
    "rank": 5
  },
  {
    "date": "2024-01-16",
    "rank": 3
  }
]
```

---

## Step 5: Test Responsive Design

### Desktop (> 768px)
- Graphs should appear side-by-side (2 columns)
- Each graph takes ~50% width

### Mobile (< 768px)
- Graphs should stack vertically
- Each graph takes full width
- Still readable and interactive

### Test Method
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Try different screen sizes:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1920px)

---

## Step 6: Test Loading States

### Method 1: Slow Network Simulation
1. Open DevTools > Network tab
2. Set throttling to "Slow 3G"
3. Refresh page
4. You should see "Loading your progress data..." message

### Method 2: Inspect React Query DevTools
1. React Query DevTools should show query states
2. Check for `['user', 'scoreHistory']` and `['user', 'rankHistory']` queries

---

## Troubleshooting

### Score Graph Not Showing Data
- ✅ Check: Have you submitted any answers?
- ✅ Check: Is backend running?
- ✅ Check: Browser console for errors
- ✅ Check: Network tab - is `/api/v1/user/score-history` returning data?

### Rank Graph Not Showing Data
- ✅ Check: Have you run the snapshot script?
- ✅ Check: Does `rank_history` collection exist in Firestore?
- ✅ Check: Are there documents for your user ID?
- ✅ Check: Network tab - is `/api/v1/leaderboard/rank-history` returning data?

### Graphs Not Appearing on HomePage
- ✅ Check: Are you logged in?
- ✅ Graphs only show for authenticated users

### Script Fails to Run
- ✅ Check: Is Firebase service account key configured?
- ✅ Check: Are there users in the `leaderboard` collection?
- ✅ Run with: `python -m app.scripts.snapshot_ranks` from `tonequest_backend` directory

### Y-Axis Not Inverted on Rank Graph
- ✅ Check: Is `reversed={true}` set on YAxis in RankHistoryChart.tsx?
- ✅ Verify: Rank 1 should appear at the top of the graph

---

## Success Criteria

✅ Score graph displays with attempt numbers on X-axis
✅ Question ID appears in tooltip (not on X-axis)
✅ Rank graph Y-axis is inverted (rank 1 at top)
✅ Both graphs appear on UserInfoPage and HomePage
✅ Graphs are responsive on mobile/tablet/desktop
✅ Empty states show appropriate messages
✅ Loading states work correctly
✅ Snapshot script runs without errors
✅ API endpoints return correct data format

---

## Sample Test Scenario

1. **Day 1 (Today)**:
   - Create account and log in
   - Submit 3 answers
   - Run snapshot script: `python -m app.scripts.snapshot_ranks`
   - View graphs: Score graph shows 3 points, Rank graph shows 1 point

2. **Day 2 (Tomorrow)**:
   - Submit 2 more answers
   - Run snapshot script again (or wait for cron)
   - View graphs: Score graph shows 5 points, Rank graph shows 2 points

3. **Day 3 (Day After)**:
   - Submit 1 more answer
   - Run snapshot script
   - View graphs: Score graph shows 6 points, Rank graph shows 3 points
   - Observe rank progression over time

---

Happy Testing! 🚀
