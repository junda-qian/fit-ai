# User Profile Schema - Complete Specification

## Overview

This document defines the complete `user_profiles` schema needed for the multi-agent fitness system.

---

## Current vs Required Fields

### ✅ Already Exists (No Changes Needed)

| Field | Type | Description | Used By |
|-------|------|-------------|---------|
| `id` | string | Unique profile ID (UUID) | All |
| `user_id` | string | User identifier | All |
| `target_calories` | int | Daily calorie target | Nutrition tracking |
| `target_protein` | float | Daily protein target (g) | Nutrition tracking |
| `target_carbs` | float | Daily carbs target (g) | Nutrition tracking |
| `target_fats` | float | Daily fats target (g) | Nutrition tracking |
| `bmr` | float | Basal Metabolic Rate | Energy calculations |
| `tdee` | float | Total Daily Energy Expenditure | Energy calculations |
| `activity_level` | float | Physical activity multiplier (1.1-1.9) | Energy calculations |
| `body_weight_kg` | float | Current body weight (kg) | All agents |
| `body_fat_pct` | float | Current body fat percentage | Nutrition Agent |
| `created_at` | datetime | Profile creation timestamp | Communication Agent |
| `updated_at` | datetime | Last update timestamp | All |

### ⚠️ Needs Update

| Field | Current Value | New Value | Reason |
|-------|--------------|-----------|---------|
| `goal` | "bulk", "cut", "maintain" | "lose_weight", "build_muscle", "maintain" | Match agent spec terminology |

### 🆕 Missing Fields (Must Add)

| Field | Type | Required | Default | Description | Used By |
|-------|------|----------|---------|-------------|---------|
| `sex` | string | ✅ Yes | - | "male" or "female" | Nutrition Agent (Table 1) |
| `training_status` | string | ✅ Yes | "novice" | "novice", "intermediate", "advanced" | Nutrition Agent (Table 3), Communication Agent |
| `height_cm` | float | ⚠️ Optional | null | Height in cm (for Navy method BF% calc) | Body composition |
| `age` | int | ⚠️ Optional | null | Age in years (for future BMR methods) | Energy calculations |
| `name` | string | ⚠️ Optional | null | User's first name | Communication Agent (personalization) |
| `is_active` | bool | ✅ Yes | true | Whether user is active (for filtering in weekly analysis) | Nutrition Agent |
| `communication_style` | string | ⚠️ Optional | "encouraging" | "encouraging", "direct", "scientific" | Communication Agent |
| `language` | string | ⚠️ Optional | "en" | Language code (ISO 639-1) | Communication Agent |
| `enable_ai_reasoning` | bool | ⚠️ Optional | false | Feature flag for AI reasoning enhancement | Future feature |
| `onboarding_completed` | bool | ⚠️ Optional | false | Whether user completed onboarding | Frontend |
| `timezone` | string | ⚠️ Optional | "UTC" | User timezone (e.g., "America/New_York") | Scheduling |

---

## Complete Schema Definition

### Pydantic Model (Updated)

```python
# backend/models.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4


class UserProfile(BaseModel):
    """
    Complete user profile for multi-agent fitness system.

    Stores:
    - Personal info (name, age, sex, height, weight)
    - Fitness targets (calories, macros, BMR, TDEE)
    - Training status and goals
    - Communication preferences
    - Account status
    """
    # ===== Identifiers =====
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str

    # ===== Personal Information =====
    name: Optional[str] = None  # First name for personalization
    age: Optional[int] = None  # For BMR calculations
    sex: str  # "male" or "female" - REQUIRED for Nutrition Agent
    height_cm: Optional[float] = None  # For Navy method body fat calculation

    # ===== Current Metrics =====
    body_weight_kg: float
    body_fat_pct: float

    # ===== Fitness Goals =====
    goal: Literal["lose_weight", "build_muscle", "maintain"]  # Changed from "bulk"/"cut"
    training_status: Literal["novice", "intermediate", "advanced"] = "novice"

    # ===== Nutrition Targets (Updated by Nutrition Agent) =====
    target_calories: int
    target_protein: float
    target_carbs: float
    target_fats: float

    # ===== Energy Calculations =====
    bmr: float  # Basal Metabolic Rate
    tdee: float  # Total Daily Energy Expenditure
    activity_level: float  # Physical activity multiplier (1.1-1.9)

    # ===== Communication Preferences =====
    communication_style: Literal["encouraging", "direct", "scientific"] = "encouraging"
    language: str = "en"  # ISO 639-1 language code

    # ===== Feature Flags =====
    enable_ai_reasoning: bool = False  # Future: AI enhancement of recommendations
    is_active: bool = True  # Filter for weekly analysis

    # ===== Account Status =====
    onboarding_completed: bool = False
    timezone: str = "UTC"  # IANA timezone (e.g., "America/New_York")

    # ===== Timestamps =====
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator('sex')
    @classmethod
    def validate_sex(cls, v: str) -> str:
        """Validate sex is either male or female"""
        if v.lower() not in ["male", "female"]:
            raise ValueError("sex must be 'male' or 'female'")
        return v.lower()

    @field_validator('body_fat_pct')
    @classmethod
    def validate_body_fat_pct(cls, v: float) -> float:
        """Validate body fat percentage is reasonable"""
        if not 3 <= v <= 60:
            raise ValueError("body_fat_pct must be between 3% and 60%")
        return v

    @field_validator('training_status')
    @classmethod
    def validate_training_status(cls, v: str) -> str:
        """Validate training status"""
        if v.lower() not in ["novice", "intermediate", "advanced"]:
            raise ValueError("training_status must be 'novice', 'intermediate', or 'advanced'")
        return v.lower()


class UserProfileCreate(BaseModel):
    """
    Request model for creating user profile.

    Minimal required fields for onboarding.
    """
    user_id: str

    # Required personal info
    sex: str
    body_weight_kg: float
    body_fat_pct: float
    goal: Literal["lose_weight", "build_muscle", "maintain"]

    # Optional personal info
    name: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None

    # Energy calculation results (from frontend calculator)
    target_calories: int
    target_protein: float
    target_carbs: float
    target_fats: float
    bmr: float
    tdee: float
    activity_level: float

    # Optional preferences
    training_status: Literal["novice", "intermediate", "advanced"] = "novice"
    communication_style: Literal["encouraging", "direct", "scientific"] = "encouraging"
    language: str = "en"
    timezone: str = "UTC"


class UserProfileUpdate(BaseModel):
    """
    Request model for updating user profile.
    All fields optional (partial update).
    """
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    body_weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    goal: Optional[Literal["lose_weight", "build_muscle", "maintain"]] = None
    training_status: Optional[Literal["novice", "intermediate", "advanced"]] = None
    target_calories: Optional[int] = None
    target_protein: Optional[float] = None
    target_carbs: Optional[float] = None
    target_fats: Optional[float] = None
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    activity_level: Optional[float] = None
    communication_style: Optional[Literal["encouraging", "direct", "scientific"]] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None
    enable_ai_reasoning: Optional[bool] = None
    onboarding_completed: Optional[bool] = None
    timezone: Optional[str] = None
```

---

## DynamoDB Schema

```python
{
    # ===== Identifiers =====
    "id": "9b66a3a1-e474-47f4-8f4c-938d87d98120",  # Partition key
    "user_id": "user_123",  # GSI partition key for user lookup

    # ===== Personal Information =====
    "name": "Alex",  # NEW
    "age": 28,  # NEW
    "sex": "male",  # NEW - REQUIRED
    "height_cm": 175.0,  # NEW

    # ===== Current Metrics =====
    "body_weight_kg": 85.0,
    "body_fat_pct": 20.0,

    # ===== Fitness Goals =====
    "goal": "lose_weight",  # UPDATED: was "cut", now "lose_weight"
    "training_status": "intermediate",  # NEW - REQUIRED

    # ===== Nutrition Targets =====
    "target_calories": 2200,
    "target_protein": 170.0,
    "target_carbs": 220.0,
    "target_fats": 73.0,

    # ===== Energy Calculations =====
    "bmr": 1850.0,
    "tdee": 2640.0,
    "activity_level": 1.4,

    # ===== Communication Preferences =====
    "communication_style": "encouraging",  # NEW
    "language": "en",  # NEW

    # ===== Feature Flags =====
    "enable_ai_reasoning": false,  # NEW
    "is_active": true,  # NEW - REQUIRED

    # ===== Account Status =====
    "onboarding_completed": true,  # NEW
    "timezone": "America/Los_Angeles",  # NEW

    # ===== Timestamps =====
    "created_at": "2025-08-04T00:00:00Z",
    "updated_at": "2025-11-02T09:04:48.791168Z"
}
```

### Global Secondary Index (GSI)

**Name**: `user_id-index`
- **Partition Key**: `user_id`
- **Purpose**: Fast lookup by user_id (most common query pattern)

---

## Migration Strategy

### Step 1: Add New Fields with Defaults

```python
# migration_script.py

def migrate_user_profiles():
    """
    Add new fields to existing user profiles.
    Safe to run multiple times (idempotent).
    """
    profiles = db.user_profiles.find_all()

    for profile in profiles:
        updates = {}

        # Add missing required fields with sensible defaults
        if "sex" not in profile:
            updates["sex"] = "male"  # Default - user should update in settings

        if "training_status" not in profile:
            # Infer from workout history if possible
            weeks_training = calculate_weeks_since_first_workout(profile["user_id"])
            if weeks_training < 26:  # < 6 months
                updates["training_status"] = "novice"
            elif weeks_training < 104:  # < 2 years
                updates["training_status"] = "intermediate"
            else:
                updates["training_status"] = "advanced"

        if "is_active" not in profile:
            # Check if user logged data in last 30 days
            last_log = get_last_activity(profile["user_id"])
            updates["is_active"] = (datetime.now() - last_log).days < 30

        # Add optional fields with defaults
        if "communication_style" not in profile:
            updates["communication_style"] = "encouraging"

        if "language" not in profile:
            updates["language"] = "en"

        if "enable_ai_reasoning" not in profile:
            updates["enable_ai_reasoning"] = False

        if "onboarding_completed" not in profile:
            updates["onboarding_completed"] = True  # Existing users already onboarded

        if "timezone" not in profile:
            updates["timezone"] = "UTC"

        # Update goal terminology
        if profile.get("goal") == "bulk":
            updates["goal"] = "build_muscle"
        elif profile.get("goal") == "cut":
            updates["goal"] = "lose_weight"
        # "maintain" stays as is

        # Apply updates
        if updates:
            db.user_profiles.update(profile["id"], updates)
            print(f"Migrated profile {profile['user_id']}: {updates.keys()}")
```

### Step 2: Update Frontend Forms

Add fields to user settings/onboarding:
- Sex (required dropdown: Male/Female)
- Training Status (optional dropdown: Novice/Intermediate/Advanced)
- Communication Style (optional: Encouraging/Direct/Scientific)
- Name (optional text input)

### Step 3: Update API Endpoints

```python
# backend/server.py

@app.put("/api/user-profile/{user_id}")
async def update_user_profile(user_id: str, update: UserProfileUpdate):
    """
    Update user profile (partial update supported).
    """
    # Validate
    existing = db.user_profiles.find_one({"user_id": user_id})
    if not existing:
        raise HTTPException(404, "User profile not found")

    # Apply updates
    update_data = update.dict(exclude_unset=True)  # Only fields provided
    update_data["updated_at"] = datetime.now()

    db.user_profiles.update(existing["id"], update_data)

    return {"message": "Profile updated", "updated_fields": list(update_data.keys())}
```

---

## Usage by Agents

### Nutrition Agent

**Required fields:**
- `sex` → Table 1 (optimal deficit by body fat % and sex)
- `training_status` → Table 3 (optimal surplus by training status)
- `body_fat_pct` → Table 1 & 2 (deficit calculation)
- `goal` → Determine if cutting or bulking
- `is_active` → Filter users for weekly analysis

**Example query:**
```python
# Get all active users for weekly analysis
active_users = db.user_profiles.find({
    "is_active": True
})
```

### Training Agent

**Required fields:**
- `training_status` → Determines progression expectations
- `user_id` → Link to exercises and workout logs

### Communication Agent

**Required fields:**
- `name` → Personalize message ("Hey Alex!")
- `communication_style` → Adjust tone
- `language` → Localization
- `created_at` → Calculate weeks_on_program
- `goal` → Context for messaging

**Example context building:**
```python
weeks_on_program = (datetime.now() - user["created_at"]).days // 7

message_context = {
    "name": user.get("name", "there"),  # Fallback to "there" if no name
    "weeks_on_program": weeks_on_program,
    "goal": user["goal"],
    "communication_style": user.get("communication_style", "encouraging"),
    "language": user.get("language", "en")
}
```

---

## Validation Rules

### Required Validations
- `sex`: Must be "male" or "female"
- `body_fat_pct`: Must be 3-60%
- `body_weight_kg`: Must be > 0
- `training_status`: Must be "novice", "intermediate", or "advanced"
- `goal`: Must be "lose_weight", "build_muscle", or "maintain"
- `communication_style`: Must be "encouraging", "direct", or "scientific"

### Recommended Validations
- `age`: 13-100 (if provided)
- `height_cm`: 100-250 (if provided)
- `target_calories`: 1000-5000
- `activity_level`: 1.1-1.9

---

## Frontend Changes Required

### 1. Onboarding Flow
Add to initial setup:
```
Step 1: Basic Info
  - Name (optional)
  - Sex (required) ← NEW
  - Age (optional)
  - Height (optional)
  - Current weight
  - Body fat % (or estimate)

Step 2: Goals
  - Goal: Lose Weight / Build Muscle / Maintain
  - Training experience: Novice / Intermediate / Advanced ← NEW

Step 3: Preferences
  - Communication style: Encouraging / Direct / Scientific ← NEW
  - Timezone selection ← NEW
```

### 2. Settings Page
Add editable fields:
- Personal info (name, age, sex, height)
- Training status
- Communication preferences
- Account status (is_active toggle)

### 3. Profile Display
Show:
- Training status badge ("Novice", "Intermediate", "Advanced")
- Weeks on program (calculated from created_at)
- Communication style

---

## Testing

### Unit Tests

```python
def test_user_profile_validation():
    """Test user profile validations"""
    # Valid profile
    profile = UserProfile(
        user_id="test_123",
        sex="male",
        body_weight_kg=80.0,
        body_fat_pct=15.0,
        goal="lose_weight",
        training_status="intermediate",
        target_calories=2200,
        target_protein=160.0,
        target_carbs=220.0,
        target_fats=73.0,
        bmr=1850.0,
        tdee=2400.0,
        activity_level=1.3
    )
    assert profile.sex == "male"
    assert profile.training_status == "intermediate"

    # Invalid sex
    with pytest.raises(ValueError):
        UserProfile(sex="other", ...)  # Should fail

    # Invalid body fat %
    with pytest.raises(ValueError):
        UserProfile(body_fat_pct=70, ...)  # Should fail

def test_goal_migration():
    """Test goal terminology migration"""
    # Old terminology
    old_profile = {"goal": "bulk"}

    # After migration
    migrated = migrate_goal(old_profile)
    assert migrated["goal"] == "build_muscle"
```

---

## Summary

### Changes Required:
1. ✅ **Add 11 new fields** to UserProfile model
2. ✅ **Update 1 field** (goal terminology)
3. ✅ **Create migration script** for existing users
4. ✅ **Update frontend** (onboarding + settings)
5. ✅ **Update API** (support partial updates)

### Impact:
- **Breaking change**: `goal` values changed ("bulk" → "build_muscle", "cut" → "lose_weight")
- **Migration required**: All existing profiles need new required fields (`sex`, `training_status`, `is_active`)
- **Frontend updates**: Onboarding and settings pages need new fields

### Timeline:
- Migration script: 1-2 hours
- Backend model updates: 1 hour
- Frontend updates: 4-6 hours
- Testing: 2-3 hours
- **Total: 1-2 days**
