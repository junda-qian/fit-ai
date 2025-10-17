# Workout Planner

## Total Training Volume Per Week Per Muscle

### Elements to Decide Optimal Volume
- Training Status (1 = Novice, 2 = Intermediate, 3 = Advanced)
- Sex (0 = Male, 1 = Female)
- Recovery Factor (0.5 - 1.2)
- Energy Balance Factor
- Age
- Training Frequency (how often trains per week)

### How to Calculate Estimated Optimal Sets Per Week Per Muscle Group

```
= ((IF(Training Frequency < 3, Training Frequency, 2.5)) * 5) * Recovery Factor
  * Energy Balance Factor
  * SQRT(Training Status)
  * (1 - ((MAX(Age - 50, 0)) / 10 * 0.12))
  + Sex * 3
```

### Training Dedication Level

Choose your training approach based on your priorities:

**A: Sustainability Focus**
- *"Sustainability is most important to me. As long as I'm moving in the right direction, I don't care about the rate of progress."*
- **Target volume:** Around 60% - 75% of estimated optimal sets

**B: Balanced Approach**
- *"I want to strike a reasonable balance between good results in proportion to effort and sustainability."*
- **Target volume:** Around 75% - 90% of estimated optimal sets

**C: Maximum Results**
- *"I will do whatever it takes to achieve maximum results without compromising my health."*
- **Target volume:** Around 90% - 100% of estimated optimal sets

## Training Intensity Guidelines

### Novice
- **Compound exercises:** 60% intensity
- **Isolation exercises:** 60% intensity

### Intermediate
- **Compound exercises:** 80% intensity
- **Isolation exercises:** 65% intensity

### Advanced
- **Compound exercises:** 85% intensity
- **Isolation exercises:** 70% intensity

## Exercise Muscle Group Activation Matrix

| Exercise | Pecs | Delt | Traps | Lats | Biceps | Triceps | Erector Spine | Quadriceps | Hamstrings | Glutes | Calves | Abs |
|----------|------|------|-------|------|--------|---------|---------------|------------|------------|--------|--------|-----|
| Powerlifting deadlift | | | 1 | 0.25 | | | 1 | 0.5 | 0.75 | 1 | 0.5 | 0.25 |
| Romanian deadlifts | | | 1 | 0.25 | | | 1 | | 1 | 1 | | 0.25 |
| Goodmornings | | | | | | | 1 | | 1 | 1 | | 0.25 |
| Hip extensions & pull-throughs | | | | | | | 0.25 | | 1 | 1 | | |
| Back extensions | | | | | | | 1 | | 1 | 1 | | |
| Leg curls | | | | | | | | | 1 | | 1 | |
| Barbell squats | | | | | | | 1 | 1 | | 1 | 0.5 | 0.25 |
| Leg presses, hack & belt squats | | | | | | | 0.25 | 1 | | 1 | 0.5 | |
| Bulgarian split squats | | | | | | | 0.5 | 1 | | 1 | 0.5 | 0.25 |
| Lunges & step-ups | | | | | | | 0.5 | 1 | | 1 | 0.5 | 0.25 |
| Leg extensions | | | | | | | | 1 | | | | |
| Hip thrusts & glute kickbacks | | | | | | | | 0.5 | | 1 | | |
| Hip abduction | | | | | | | | | | 1 | | |
| Calf raises/jumps | | | | | | | | | | | 1 | |
| Seated calf raises | | | | | | | | | | | 1 | |
| Chin-ups & pulldowns | 0.25 | 1 | 1 | 1 | 1 | | | | | | | |
| Pull-ups & wide pulldowns | 0.5 | 0.25 | 1 | 1 | 1 | | | | | | | |
| Cable rows with spinal flexion | | 1 | 1 | 1 | 0.5 | 0.25 | 0.5 | | 0.25 | 0.25 | | |
| Pull-overs & lat prayers | 0.5 | 1 | | 1 | | 1 | | | | | | |
| High rows & rear delt flys | | 1 | 1 | | | | | | | | | |
| Barbell bench press | 1 | 1 | | | | 1 | | | | | | |
| Dumbbell bench press | 1 | 1 | | | | 0.5 | | | | | | |
| Chest flys | 1 | 1 | | | | | | | | | | |
| Barbell overhead press | 0.25 | 1 | 0.25 | | | 1 | | | | | | 0.25 |
| Dumbbell overhead press | 0.25 | 1 | 0.25 | | | 0.5 | | | | | | 0.25 |
| Lateral raises | 0.25 | 1 | 0.25 | | | | | | | | | |
| Shrugs | | | 1 | | | | | | | | | |
| Triceps extensions | | | | | | 1 | | | | | | |
| Biceps curls | | | | | 1 | | | | | | | |
| Ab crunches | | | | | | | | | | | | 1 |

---

**Legend:**
- 1 = Primary muscle activation
- 0.75 = High secondary activation
- 0.5 = Moderate secondary activation
- 0.25 = Minor secondary activation
- Empty cell = No significant activation

## Exercise Classification

| Exercise | Type |
|----------|------|
| Powerlifting deadlift | Compound |
| Romanian deadlifts | Compound |
| Goodmornings | Compound |
| Hip extensions & pull-throughs | Compound |
| Back extensions | Isolation |
| Leg curls | Isolation |
| Barbell squats | Compound |
| Leg presses, hack & belt squats | Compound |
| Bulgarian split squats | Compound |
| Lunges & step-ups | Compound |
| Leg extensions | Isolation |
| Hip thrusts & glute kickbacks | Compound (hip thrusts) / Isolation (glute kickbacks) |
| Hip abduction | Isolation |
| Calf raises/jumps | Compound (jumps) / Isolation (calf raises) |
| Seated calf raises | Isolation |
| Chin-ups & pulldowns | Compound |
| Pull-ups & wide pulldowns | Compound |
| Cable rows with spinal flexion | Compound |
| Pull-overs & lat prayers | Pull-overs: Compound / Lat prayers: Isolation |
| High rows & rear delt flys | High rows: Compound / Rear delt flys: Isolation |
| Barbell bench press | Compound |
| Dumbbell bench press | Compound |
| Chest flys | Isolation |
| Barbell overhead press | Compound |
| Dumbbell overhead press | Compound |
| Lateral raises | Isolation |
| Shrugs | Isolation |
| Triceps extensions | Isolation |
| Biceps curls | Isolation |
| Ab crunches | Isolation |

## Prerequisites to Create Workout Plan

Before creating a workout plan, ensure the following requirements are met:

### Required User Input
- **Estimated Optimal Sets Per Week Per Muscle Group** (calculated based on user's training status, sex, recovery factor, energy balance factor, age, and training frequency)
- **Weekly Target Volume** (Weekly Target Sets) based on user's dedication level (A, B, or C)

### Workout Plan Must Include Only
- **Categorization of sets** for each training day (e.g., Day A, Day B, Day C)
- **Frequency** of each category (e.g., 1x per week, 2x per week)
- **Exercise Name**
- **Number of sets** for each exercise
- **Intensity** percentage for each exercise

### Important Guidelines
- **Weekly sets** for each muscle group listed in the Exercise Muscle Group Activation Matrix should be around the weekly target volume
- **Exercises** should only be selected from the Exercise Muscle Group Activation Matrix
- **Training intensity** should be determined based on the Training Intensity Guidelines and the Exercise Classification
- **Training volume** (training sets) per muscle per day should not exceed 10 sets
- **Training frequency constraint**: The sum of all workout day frequencies in the plan must NOT exceed the user's input training frequency. The input training frequency represents the MAXIMUM number of days per week the user is willing to commit to training. The actual workout plan can use fewer days as long as volume targets are met.
- Refer to the Generated Training Plan Sample below as a reference when creating new plans

## Generated Training Plan Sample

### Sample Input
- **Training Status:** 1 (Novice)
- **Sex:** 0 (Male)
- **Recovery Factor:** 1.0
- **Energy Balance Factor:** 1.1
- **Age:** 28
- **Training Frequency:** 6 days/week
- **Dedication Level:** A

### Calculation and Reasoning
- **Estimated Optimal Sets Per Week Per Muscle Group:** 14 (based on the input values)
- **Dedication Level A:** Target volume is 60% - 75% of estimated optimal sets
- **Target Range:** Around 8.4 - 10.5 sets per week per muscle group

### Training Output Sample

Format: `Number of Sets x Intensity% - Exercise Name - Training Volume per Muscle`

#### Day A (2x/week)
- 4 x 60% - Barbell bench press - 1 Pecs, 1 Delt, 1 Triceps
- 3 x 60% - Ab crunches - 1 Abs
- 2 x 60% - Bicep curls - 1 Biceps

#### Day B (2x/week)
- 3 x 60% - Pull-ups - 0.5 Pecs, 0.25 Delt, 1 Traps, 1 Lats, 1 Biceps
- 2 x 60% - Romanian deadlifts - 1 Traps, 0.25 Lats, 1 Erector Spine, 1 Hamstrings, 1 Glutes, 0.25 Abs

#### Day C (2x/week)
- 4 x 60% - Barbell squats - 1 Erector Spine, 1 Quadriceps, 1 Glutes, 0.5 Calves, 0.25 Abs
- 4 x 60% - Leg curls - 1 Hamstrings, 1 Calves
- 3 x 60% - Calf raises - 1 Calves

### Weekly Volumes Based on Training Output

Target: 8.4 - 10.5 sets per week per muscle group

| Muscle Group | Weekly Sets |
|--------------|-------------|
| Pecs | 11 |
| Delt | 9.5 |
| Traps | 10 |
| Lats | 10 |
| Biceps | 10 |
| Triceps | 8 |
| Erector Spine | 10 |
| Quadriceps | 8 |
| Hamstrings | 10 |
| Glutes | 10 |
| Calves | 10 |
| Abs | 9 |
