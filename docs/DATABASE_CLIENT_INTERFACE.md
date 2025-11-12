# Database Client Interface Specification

## Overview

This document defines the complete database client interface (`db`) used by all agents and backend services.

**Design Goals:**
- Single interface works for both JSONDatabase (dev) and DynamoDB (prod)
- Type-safe, well-documented methods
- Optimized query patterns for DynamoDB
- Easy to test and mock

---

## Current Implementation Status

### ✅ Base Methods (Already Implemented)

| Method | Signature | Description |
|--------|-----------|-------------|
| `insert()` | `insert(collection: str, document: Dict) -> Dict` | Insert a document |
| `find_one()` | `find_one(collection: str, query: Dict) -> Optional[Dict]` | Find single document |
| `find()` | `find(collection: str, query: Dict) -> List[Dict]` | Find all matching documents |
| `update()` | `update(collection: str, query: Dict, update: Dict) -> bool` | Update documents |
| `delete()` | `delete(collection: str, query: Dict) -> int` | Delete documents |

### 🆕 Agent-Specific Methods (Need to Add)

Methods needed by Nutrition, Training, and Communication agents.

---

## Extended Database Client

### Collection-Specific Interfaces

Instead of generic `db.find("user_profiles", {...})`, provide collection-specific methods:

```python
# Much cleaner:
db.user_profiles.find_all_active()
db.body_logs.find_recent(user_id, days=14)
db.weekly_analyses.find_latest(user_id)

# vs old way:
db.find("user_profiles", {"is_active": True})
db.find("body_logs", {"user_id": user_id})  # + manual date filtering
```

---

## User Profiles Collection

### Methods

```python
class UserProfilesCollection:
    """User profiles collection interface"""

    def find_all_active(self) -> List[Dict]:
        """
        Find all active users for weekly analysis.

        Returns:
            List of user profiles where is_active=True

        Example:
            users = db.user_profiles.find_all_active()
            # [{"user_id": "user_123", "is_active": True, ...}, ...]
        """

    def find_by_user_id(self, user_id: str) -> Optional[Dict]:
        """
        Find user profile by user_id.

        Args:
            user_id: User identifier

        Returns:
            User profile or None if not found

        Example:
            profile = db.user_profiles.find_by_user_id("user_123")
        """

    def update_targets(self, user_id: str, targets: Dict) -> bool:
        """
        Update nutrition targets for user.

        Args:
            user_id: User identifier
            targets: Dict with target_calories, target_protein, etc.

        Returns:
            True if updated, False if user not found

        Example:
            db.user_profiles.update_targets("user_123", {
                "target_calories": 2000,
                "target_protein": 160,
                "target_carbs": 200,
                "target_fats": 67
            })
        """

    def mark_inactive(self, user_id: str) -> bool:
        """
        Mark user as inactive (exclude from weekly analysis).

        Args:
            user_id: User identifier

        Returns:
            True if updated

        Example:
            db.user_profiles.mark_inactive("user_123")
        """
```

### Implementation

```python
# backend/database.py

class UserProfilesCollection:
    def __init__(self, db):
        self.db = db

    def find_all_active(self) -> List[Dict]:
        """Find all active users"""
        return self.db.find("user_profiles", {"is_active": True})

    def find_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Find user by user_id"""
        return self.db.find_one("user_profiles", {"user_id": user_id})

    def update_targets(self, user_id: str, targets: Dict) -> bool:
        """Update nutrition targets"""
        return self.db.update(
            "user_profiles",
            {"user_id": user_id},
            {**targets, "updated_at": datetime.now().isoformat()}
        )

    def mark_inactive(self, user_id: str) -> bool:
        """Mark user as inactive"""
        return self.db.update(
            "user_profiles",
            {"user_id": user_id},
            {"is_active": False}
        )
```

---

## Body Logs Collection

### Methods

```python
class BodyLogsCollection:
    """Body measurements and weight tracking"""

    def find_recent(self, user_id: str, days: int = 14) -> List[Dict]:
        """
        Find recent body logs for trend analysis.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            List of body logs sorted by date (oldest to newest)

        Example:
            logs = db.body_logs.find_recent("user_123", days=14)
            # [
            #   {"date": "2025-11-01", "weight": 78.5, "skinfold_sum": 50},
            #   {"date": "2025-11-03", "weight": 78.4, "skinfold_sum": 49},
            #   ...
            # ]
        """

    def find_by_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """
        Find body logs in date range.

        Args:
            user_id: User identifier
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of body logs sorted by date

        Example:
            from datetime import date
            logs = db.body_logs.find_by_date_range(
                "user_123",
                date(2025, 10, 1),
                date(2025, 10, 31)
            )
        """

    def get_latest(self, user_id: str) -> Optional[Dict]:
        """
        Get most recent body log.

        Args:
            user_id: User identifier

        Returns:
            Latest body log or None

        Example:
            latest = db.body_logs.get_latest("user_123")
            # {"date": "2025-11-12", "weight": 78.0, ...}
        """
```

### Implementation

```python
class BodyLogsCollection:
    def __init__(self, db):
        self.db = db

    def find_recent(self, user_id: str, days: int = 14) -> List[Dict]:
        """Find recent body logs"""
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        all_logs = self.db.find("body_logs", {"user_id": user_id})

        # Filter by date and sort
        recent_logs = [
            log for log in all_logs
            if self._parse_date(log["date"]) >= cutoff_date
        ]

        # Sort by date (oldest to newest)
        recent_logs.sort(key=lambda x: self._parse_date(x["date"]))

        return recent_logs

    def find_by_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Find logs in date range"""
        all_logs = self.db.find("body_logs", {"user_id": user_id})

        # Filter by date range
        filtered = [
            log for log in all_logs
            if start_date <= self._parse_date(log["date"]) <= end_date
        ]

        # Sort by date
        filtered.sort(key=lambda x: self._parse_date(x["date"]))

        return filtered

    def get_latest(self, user_id: str) -> Optional[Dict]:
        """Get most recent log"""
        all_logs = self.db.find("body_logs", {"user_id": user_id})

        if not all_logs:
            return None

        # Sort by date (newest first) and return first
        all_logs.sort(key=lambda x: self._parse_date(x["date"]), reverse=True)
        return all_logs[0]

    def _parse_date(self, date_val) -> date:
        """Parse date from various formats"""
        from datetime import date, datetime

        if isinstance(date_val, date):
            return date_val
        elif isinstance(date_val, str):
            return datetime.fromisoformat(date_val).date()
        else:
            raise ValueError(f"Invalid date format: {date_val}")
```

---

## Nutrition Logs Collection

### Methods

```python
class NutritionLogsCollection:
    """Daily nutrition tracking"""

    def find_recent(self, user_id: str, days: int = 14) -> List[Dict]:
        """
        Find recent nutrition logs.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            List of nutrition logs sorted by date

        Example:
            logs = db.nutrition_logs.find_recent("user_123", days=14)
        """

    def get_daily_totals(
        self,
        user_id: str,
        days: int = 14
    ) -> Dict[str, Dict]:
        """
        Get daily calorie/macro totals.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            Dict mapping date -> {calories, protein, carbs, fats}

        Example:
            totals = db.nutrition_logs.get_daily_totals("user_123", days=14)
            # {
            #   "2025-11-01": {"calories": 2180, "protein": 160, ...},
            #   "2025-11-02": {"calories": 2200, "protein": 165, ...},
            #   ...
            # }
        """

    def calculate_average_intake(
        self,
        user_id: str,
        days: int = 14
    ) -> Dict[str, float]:
        """
        Calculate average daily intake.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            Dict with avg_calories, avg_protein, etc.

        Example:
            avg = db.nutrition_logs.calculate_average_intake("user_123")
            # {"avg_calories": 2185, "avg_protein": 162, "days_logged": 12}
        """
```

### Implementation

```python
class NutritionLogsCollection:
    def __init__(self, db):
        self.db = db

    def find_recent(self, user_id: str, days: int = 14) -> List[Dict]:
        """Find recent nutrition logs"""
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        all_logs = self.db.find("nutrition_logs", {"user_id": user_id})

        recent_logs = [
            log for log in all_logs
            if self._parse_date(log["date"]) >= cutoff_date
        ]

        recent_logs.sort(key=lambda x: self._parse_date(x["date"]))

        return recent_logs

    def get_daily_totals(
        self,
        user_id: str,
        days: int = 14
    ) -> Dict[str, Dict]:
        """Get daily totals"""
        logs = self.find_recent(user_id, days)

        # Group by date
        daily_totals = {}
        for log in logs:
            log_date = str(self._parse_date(log["date"]))

            if log_date not in daily_totals:
                daily_totals[log_date] = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fats": 0
                }

            daily_totals[log_date]["calories"] += log["calories"]
            daily_totals[log_date]["protein"] += log["protein"]
            daily_totals[log_date]["carbs"] += log["carbs"]
            daily_totals[log_date]["fats"] += log["fats"]

        return daily_totals

    def calculate_average_intake(
        self,
        user_id: str,
        days: int = 14
    ) -> Dict[str, float]:
        """Calculate average daily intake"""
        daily_totals = self.get_daily_totals(user_id, days)

        if not daily_totals:
            return {
                "avg_calories": 0,
                "avg_protein": 0,
                "avg_carbs": 0,
                "avg_fats": 0,
                "days_logged": 0
            }

        total_days = len(daily_totals)
        sum_calories = sum(d["calories"] for d in daily_totals.values())
        sum_protein = sum(d["protein"] for d in daily_totals.values())
        sum_carbs = sum(d["carbs"] for d in daily_totals.values())
        sum_fats = sum(d["fats"] for d in daily_totals.values())

        return {
            "avg_calories": round(sum_calories / total_days, 1),
            "avg_protein": round(sum_protein / total_days, 1),
            "avg_carbs": round(sum_carbs / total_days, 1),
            "avg_fats": round(sum_fats / total_days, 1),
            "days_logged": total_days
        }

    def _parse_date(self, date_val) -> date:
        """Parse date from various formats"""
        from datetime import date, datetime

        if isinstance(date_val, date):
            return date_val
        elif isinstance(date_val, str):
            return datetime.fromisoformat(date_val).date()
        else:
            raise ValueError(f"Invalid date format: {date_val}")
```

---

## Workout Logs Collection

### Methods

```python
class WorkoutLogsCollection:
    """Completed workout tracking"""

    def find_recent(self, user_id: str, days: int = 14) -> List[Dict]:
        """
        Find recent workout logs.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            List of workout logs sorted by date

        Example:
            logs = db.workout_logs.find_recent("user_123", days=14)
        """

    def count_sessions(self, user_id: str, days: int = 14) -> int:
        """
        Count number of workout sessions.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            Number of completed workouts

        Example:
            count = db.workout_logs.count_sessions("user_123", days=14)
            # 4
        """

    def calculate_total_volume(
        self,
        user_id: str,
        days: int = 14
    ) -> float:
        """
        Calculate total training volume (sets × reps × weight).

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            Total volume in kg

        Example:
            volume = db.workout_logs.calculate_total_volume("user_123")
            # 15000.0 (kg)
        """
```

---

## Weekly Analyses Collection (New)

### Methods

```python
class WeeklyAnalysesCollection:
    """Nutrition agent weekly analysis results"""

    def find_latest(self, user_id: str) -> Optional[Dict]:
        """
        Get most recent weekly analysis.

        Args:
            user_id: User identifier

        Returns:
            Latest analysis or None

        Example:
            analysis = db.weekly_analyses.find_latest("user_123")
            # {
            #   "week_starting": "2025-11-11",
            #   "recommendation": {...},
            #   "data_summary": {...}
            # }
        """

    def find_by_week(self, user_id: str, week_starting: str) -> Optional[Dict]:
        """
        Get analysis for specific week.

        Args:
            user_id: User identifier
            week_starting: Week starting date (ISO format)

        Returns:
            Analysis for that week or None

        Example:
            analysis = db.weekly_analyses.find_by_week("user_123", "2025-11-04")
        """

    def find_recent(self, user_id: str, limit: int = 4) -> List[Dict]:
        """
        Get recent weekly analyses.

        Args:
            user_id: User identifier
            limit: Number of analyses to return

        Returns:
            List of analyses sorted by week (newest first)

        Example:
            analyses = db.weekly_analyses.find_recent("user_123", limit=4)
        """

    def find_pending_communication(self) -> List[Dict]:
        """
        Find all analyses needing communication.

        Returns:
            List of analyses where communication_pending=True

        Example:
            pending = db.weekly_analyses.find_pending_communication()
        """
```

---

## Weekly Communications Collection (New)

### Methods

```python
class WeeklyCommunicationsCollection:
    """Communication agent message results"""

    def find_latest(self, user_id: str) -> Optional[Dict]:
        """
        Get most recent weekly communication.

        Args:
            user_id: User identifier

        Returns:
            Latest communication message or None

        Example:
            comm = db.weekly_communications.find_latest("user_123")
            # {
            #   "message": "Great week! Your weight...",
            #   "week_starting": "2025-11-11"
            # }
        """

    def find_by_week(self, user_id: str, week_starting: str) -> Optional[Dict]:
        """Get communication for specific week"""

    def find_recent(self, user_id: str, limit: int = 8) -> List[Dict]:
        """Get recent communications (history)"""
```

---

## Database Client Wrapper

### Complete Interface

```python
# backend/database.py

class FitnessDatabaseClient:
    """
    Complete database client with collection-specific interfaces.

    Usage:
        db = FitnessDatabaseClient()
        users = db.user_profiles.find_all_active()
        logs = db.body_logs.find_recent("user_123", days=14)
    """

    def __init__(self, use_dynamodb: bool = False):
        # Initialize base database
        if use_dynamodb:
            self._db = DynamoDBAdapter()
        else:
            self._db = JSONDatabase()

        # Collection-specific interfaces
        self.user_profiles = UserProfilesCollection(self._db)
        self.body_logs = BodyLogsCollection(self._db)
        self.nutrition_logs = NutritionLogsCollection(self._db)
        self.workout_logs = WorkoutLogsCollection(self._db)
        self.weekly_analyses = WeeklyAnalysesCollection(self._db)
        self.weekly_communications = WeeklyCommunicationsCollection(self._db)
        self.workout_plans = WorkoutPlansCollection(self._db)
        self.daily_summaries = DailySummariesCollection(self._db)

    # Expose base methods for backward compatibility
    def insert(self, collection: str, document: Dict) -> Dict:
        return self._db.insert(collection, document)

    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        return self._db.find_one(collection, query)

    def find(self, collection: str, query: Dict) -> List[Dict]:
        return self._db.find(collection, query)

    def update(self, collection: str, query: Dict, update: Dict) -> bool:
        return self._db.update(collection, query, update)

    def delete(self, collection: str, query: Dict) -> int:
        return self._db.delete(collection, query)


# Global instance
USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'
db = FitnessDatabaseClient(use_dynamodb=USE_DYNAMODB)
```

---

## DynamoDB Table Definitions

### New Tables Needed

```python
# terraform/dynamodb_tables.tf

# Weekly Analyses (Nutrition Agent results)
resource "aws_dynamodb_table" "weekly_analyses" {
  name         = "fitness-weekly-analyses-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "week_starting"  # ISO date (e.g., "2025-11-11")

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "week_starting"
    type = "S"
  }

  attribute {
    name = "communication_pending"
    type = "S"  # "true" or "false" (string for GSI)
  }

  # GSI for finding pending communications
  global_secondary_index {
    name            = "CommunicationPendingIndex"
    hash_key        = "communication_pending"
    range_key       = "week_starting"
    projection_type = "ALL"
  }
}

# Weekly Communications (Communication Agent results)
resource "aws_dynamodb_table" "weekly_communications" {
  name         = "fitness-weekly-communications-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "week_starting"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "week_starting"
    type = "S"
  }
}

# Active Plans (Nutrition plans)
resource "aws_dynamodb_table" "active_plans" {
  name         = "fitness-active-plans-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "plan_type"  # Always "nutrition" for now

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "plan_type"
    type = "S"
  }

  attribute {
    name = "active"
    type = "S"  # "true" or "false"
  }

  # GSI for finding active plans
  global_secondary_index {
    name            = "ActivePlansIndex"
    hash_key        = "active"
    projection_type = "ALL"
  }
}
```

---

## Migration Steps

### Step 1: Add Collection Classes

Create `backend/collections/` directory with collection-specific classes.

### Step 2: Update JSONDatabase

Add new collections to `self.collections` dict:
```python
self.collections = {
    # ... existing ...
    "weekly_analyses": self.data_dir / "weekly_analyses.json",
    "weekly_communications": self.data_dir / "weekly_communications.json",
    "active_plans": self.data_dir / "active_plans.json",
}
```

### Step 3: Update DynamoDBAdapter

Add new table mappings:
```python
self.table_mapping = {
    # ... existing ...
    "weekly_analyses": os.getenv('DYNAMODB_WEEKLY_ANALYSES'),
    "weekly_communications": os.getenv('DYNAMODB_WEEKLY_COMMUNICATIONS'),
    "active_plans": os.getenv('DYNAMODB_ACTIVE_PLANS'),
}
```

### Step 4: Test with JSON First

Test all collection methods with JSONDatabase before deploying to DynamoDB.

---

## Testing

### Unit Tests

```python
def test_body_logs_find_recent():
    """Test finding recent body logs"""
    db = FitnessDatabaseClient(use_dynamodb=False)

    # Insert test data
    for i in range(20):
        db.insert("body_logs", {
            "id": f"log_{i}",
            "user_id": "test_user",
            "date": (date.today() - timedelta(days=i)).isoformat(),
            "weight": 80.0 - (i * 0.1)
        })

    # Find recent 14 days
    recent = db.body_logs.find_recent("test_user", days=14)

    assert len(recent) == 14
    assert recent[0]["date"] < recent[-1]["date"]  # Sorted oldest to newest


def test_nutrition_logs_calculate_average():
    """Test calculating average intake"""
    db = FitnessDatabaseClient(use_dynamodb=False)

    # Insert test data
    for i in range(10):
        db.insert("nutrition_logs", {
            "id": f"log_{i}",
            "user_id": "test_user",
            "date": (date.today() - timedelta(days=i)).isoformat(),
            "calories": 2000 + (i * 10),
            "protein": 150,
            "carbs": 200,
            "fats": 70
        })

    avg = db.nutrition_logs.calculate_average_intake("test_user", days=10)

    assert avg["days_logged"] == 10
    assert 2000 <= avg["avg_calories"] <= 2100
```

---

## Summary

### What We're Adding:
1. ✅ Collection-specific interfaces (UserProfilesCollection, BodyLogsCollection, etc.)
2. ✅ Agent-specific query methods (find_recent, find_latest, etc.)
3. ✅ New tables (weekly_analyses, weekly_communications, active_plans)
4. ✅ FitnessDatabaseClient wrapper

### Benefits:
- Cleaner agent code (`db.body_logs.find_recent()` vs manual filtering)
- Type-safe, well-documented methods
- Same interface for JSON and DynamoDB
- Optimized DynamoDB query patterns
- Easy to test and mock

### Timeline:
- Collection classes: 4-6 hours
- New table definitions: 2 hours
- Testing: 3-4 hours
- **Total: 1-2 days**
