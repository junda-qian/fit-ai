# How to View 90-Day Test Data Progress Charts

## ✅ Test Data Generated Successfully!

**Test User Profile:**
- User ID: `test_user_90day`
- Starting weight: 85.0 kg
- Final weight: ~79.9 kg
- Weight loss: ~5.1 kg (6%) over 90 days
- Training: 48 workouts logged
- Nutrition: 189 meals logged (77/91 days)
- Body composition: Weekly skinfold measurements showing fat loss

---

## 🚀 View the Progress Charts

### Step 1: Start the Backend Server

```bash
cd backend
uv run uvicorn server:app --reload
```

Server will start at: http://localhost:8000

### Step 2: Start the Frontend

Open a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will start at: http://localhost:3000

### Step 3: Set Test User ID in Browser

1. Open http://localhost:3000 in your browser
2. Open browser console (F12 or Cmd+Option+I)
3. Run this command in console:

```javascript
localStorage.setItem('fit_tracker_user_id', 'test_user_90day');
```

4. Refresh the page (Cmd+R or F5)

### Step 4: View the Progress Charts

Navigate to: **http://localhost:3000/tracking/progress**

Or use the navigation menu:
- Home → Tracking Dashboard → Progress Tracking

---

## 📊 What You'll See

### **Progress Page Features:**

1. **Time Range Selector**
   - 7 days, 30 days, or **90 days** (select this!)

2. **Summary Stats Cards**
   - Weight Progress: Current, change, average
   - Nutrition: Avg calories, target, adherence %
   - Workouts: Total, active days, per week

3. **Weight Trend Chart**
   - 90-day weight progression showing ~6% fat loss
   - Purple line with data points
   - Daily fluctuations visible (realistic!)

4. **Daily Calories Chart**
   - Bar chart showing daily intake
   - Red dashed line = target (2200 cal)
   - Color-coded: Green (on track), Orange (under), Red (over)

5. **Macronutrient Breakdown**
   - Stacked bars: Protein (red), Carbs (green), Fats (yellow)
   - Shows macro distribution over time

6. **Workout Frequency Chart**
   - Blue bars = workout days
   - Gray bars = rest days
   - Shows 4x/week training pattern

---

## 📈 Test Data Details

### **Realistic Progression Features:**

✅ **Weight Loss Pattern:**
- Average 0.5%/week loss (healthy cutting rate)
- Daily fluctuations (±0.3-0.8 kg)
- Weekend water retention (higher carb days)
- Post-workout weight drops (glycogen depletion)
- Week 6 plateau (adaptive thermogenesis simulation)

✅ **Nutrition Compliance:**
- 85% tracking adherence (realistic!)
- Weekdays: 90-105% of target (good compliance)
- Weekends: 110-120% of target (social eating)
- 20% of days with no logging

✅ **Training Schedule:**
- 4x/week: Monday, Tuesday, Thursday, Friday
- 90% session adherence (some missed workouts)
- Upper/Lower split pattern

✅ **Body Composition Tracking:**
- Weekly skinfold measurements (every Monday)
- Starting sum: ~80mm
- Final sum: ~54mm (showing fat loss!)
- 7 measurement sites tracked

---

## 🎨 Chart Styling

The charts use:
- **Purple** for weight tracking
- **Orange** for nutrition/calories
- **Blue** for workouts
- **Green/Red/Yellow** for macro breakdown
- SVG-based charts (smooth, responsive)
- Hover tooltips for detailed data

---

## 🔄 Switch Back to Your User

To go back to your own user data:

```javascript
localStorage.setItem('fit_tracker_user_id', 'your_actual_user_id');
```

Or clear the test user:

```javascript
localStorage.removeItem('fit_tracker_user_id');
```

---

## 🗑️ Remove Test Data

If you want to remove the test data:

```bash
cd backend
uv run python -c "
import json
from pathlib import Path

files = ['body_logs.json', 'nutrition_logs.json', 'daily_summaries.json', 'user_profiles.json']
for filename in files:
    path = Path('data/tracking') / filename
    data = json.load(open(path))
    cleaned = [item for item in data if item.get('user_id') != 'test_user_90day']
    json.dump(cleaned, open(path, 'w'), indent=2)
print('✅ Test data removed')
"
```

---

## 💡 Use This Data For:

1. **UI/UX Testing** - See how charts handle real data
2. **Demo/Screenshots** - Show potential users what progress tracking looks like
3. **Development** - Test chart rendering with various data patterns
4. **Weekly Progress Analyzer Testing** - Use as input for AI agent development

---

## 📝 Notes

- All dates are relative to today (END_DATE = today, START_DATE = 90 days ago)
- Test user profile has full targets set (2200 cal, macros, etc.)
- Weight trajectory includes realistic noise and patterns
- Skinfold measurements show progressive fat loss (~2mm/week)
- Workout patterns match typical Upper/Lower 4-day split

Enjoy exploring the progress charts! 🎉
