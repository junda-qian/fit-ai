"""
Pydantic Models for AI Agents

Shared data models used across all agents for structured, validated outputs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


# ============================================================================
# Nutrition Agent Models
# ============================================================================

class MacroSplit(BaseModel):
    """
    Macronutrient breakdown in grams.

    Used in nutrition recommendations to specify daily macro targets.
    """
    protein_g: int = Field(..., ge=0, description="Protein in grams")
    carbs_g: int = Field(..., ge=0, description="Carbohydrates in grams")
    fat_g: int = Field(..., ge=0, description="Fats in grams")

    @field_validator('protein_g', 'carbs_g', 'fat_g')
    @classmethod
    def validate_positive(cls, v):
        """Ensure all macros are positive"""
        if v < 0:
            raise ValueError("Macros must be positive")
        return v

    def total_calories(self) -> int:
        """Calculate total calories from macros"""
        return (self.protein_g * 4) + (self.carbs_g * 4) + (self.fat_g * 9)


class NutritionRecommendation(BaseModel):
    """
    Structured output from Nutrition Specialist Agent.

    Contains current state, recommendations, and reasoning for nutrition adjustments.
    This is the primary output of the deterministic nutrition algorithm.
    """
    # Current state
    current_calorie_average: int = Field(..., description="Current average calorie intake")
    current_body_fat_pct: Optional[float] = Field(None, description="Current body fat percentage")
    observed_weekly_weight_change_pct: float = Field(..., description="Observed weekly weight change as % of bodyweight")

    # Recommendations
    recommended_calories: int = Field(..., ge=0, description="Recommended daily calorie target")
    recommended_deficit_or_surplus_pct: float = Field(..., description="Recommended deficit (-) or surplus (+) as percentage")
    optimal_deficit_or_surplus_pct: float = Field(..., description="Optimal deficit/surplus from tables")
    recommended_macros: MacroSplit = Field(..., description="Recommended macro split")

    # Decision metadata
    adjustment_category: Literal["increase", "decrease", "none"] = Field(..., description="Type of adjustment")
    reasoning: str = Field(..., description="Natural language explanation of recommendation")
    body_composition_status: Literal["fat_loss", "muscle_gain", "recomp", "maintenance"] = Field(
        ...,
        description="Current body composition trend"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation (0-1)")

    # Optional fields
    warnings: list[str] = Field(default_factory=list, description="Any warnings or caveats")
    next_review_date: Optional[str] = Field(None, description="When to review again (ISO date)")


class WeightTrend(BaseModel):
    """
    Weight trend analysis over specified timeframe.

    Used to detect plateaus and calculate rate of weight change.
    """
    days_analyzed: int = Field(..., ge=1, description="Number of days analyzed")
    data_points: int = Field(..., ge=0, description="Number of weight measurements")

    starting_weight: Optional[float] = Field(None, description="Weight at start of period (kg)")
    current_weight: Optional[float] = Field(None, description="Most recent weight (kg)")
    avg_weight: Optional[float] = Field(None, description="Average weight over period (kg)")

    total_change: float = Field(0.0, description="Total weight change (kg)")
    daily_rate: float = Field(0.0, description="Daily rate of change (kg/day)")
    weekly_rate: float = Field(0.0, description="Weekly rate of change (kg/week)")
    weekly_rate_pct: float = Field(0.0, description="Weekly rate as % of bodyweight")

    is_plateau: bool = Field(False, description="Whether weight has plateaued")
    trend: Literal["increasing", "stable", "decreasing"] = Field("stable", description="Overall trend direction")

    sufficient_data: bool = Field(False, description="Whether enough data for reliable analysis")


class BodyCompositionTrend(BaseModel):
    """
    Body composition trend analysis using multiple methods.

    Priority:
    1. Skinfold measurements (most reliable for trends)
    2. Waist circumference (simple, reliable)
    3. Body fat % estimates (less reliable)
    4. Inferred from strength + weight trends
    """
    method: Literal["skinfolds", "waist", "body_fat_pct", "inferred", "none"] = Field(
        ...,
        description="Method used for tracking"
    )
    confidence: Literal["high", "medium", "low", "none"] = Field(..., description="Confidence in measurements")

    days_analyzed: int = Field(..., ge=1, description="Number of days analyzed")
    data_points: int = Field(..., ge=0, description="Number of measurements")

    # Skinfold-specific fields
    starting_skinfold_sum_mm: Optional[float] = Field(None, description="Starting sum of skinfolds (mm)")
    current_skinfold_sum_mm: Optional[float] = Field(None, description="Current sum of skinfolds (mm)")
    total_change_mm: Optional[float] = Field(None, description="Total change in skinfolds (mm)")
    daily_rate_mm: Optional[float] = Field(None, description="Daily rate of change (mm/day)")

    # Waist-specific fields
    starting_waist_cm: Optional[float] = Field(None, description="Starting waist circumference (cm)")
    current_waist_cm: Optional[float] = Field(None, description="Current waist circumference (cm)")
    waist_change_cm: Optional[float] = Field(None, description="Total waist change (cm)")

    # Body fat % fields
    starting_body_fat_pct: Optional[float] = Field(None, description="Starting body fat %")
    current_body_fat_pct: Optional[float] = Field(None, description="Current body fat %")
    body_fat_change_pct: Optional[float] = Field(None, description="Change in body fat %")

    # General trend
    is_stable: bool = Field(False, description="Whether body composition is stable")
    trend: Literal["increasing", "stable", "decreasing"] = Field("stable", description="Fat mass trend direction")
    interpretation: str = Field(..., description="Human-readable interpretation")

    sufficient_data: bool = Field(False, description="Whether enough data for reliable analysis")


class NutritionSummary(BaseModel):
    """
    Summary of nutrition logs over a period.

    Used to calculate average intake and adherence.
    """
    days_analyzed: int = Field(..., ge=1, description="Number of days in period")
    days_logged: int = Field(..., ge=0, description="Number of days with nutrition logs")

    avg_calories: Optional[float] = Field(None, description="Average daily calories")
    avg_protein_g: Optional[float] = Field(None, description="Average daily protein (g)")
    avg_carbs_g: Optional[float] = Field(None, description="Average daily carbs (g)")
    avg_fat_g: Optional[float] = Field(None, description="Average daily fat (g)")

    compliance_pct: float = Field(0.0, ge=0, le=100, description="Compliance percentage")
    sufficient_data: bool = Field(False, description="Whether enough logs for analysis")


class WorkoutSummary(BaseModel):
    """
    Summary of workout logs over a period.

    Used for bulking assessment and strength progression analysis.
    """
    days_analyzed: int = Field(..., ge=1, description="Number of days analyzed")
    sessions: int = Field(..., ge=0, description="Number of workout sessions")

    total_volume_kg: float = Field(0.0, description="Total training volume (sets × reps × weight)")
    avg_session_volume_kg: Optional[float] = Field(None, description="Average volume per session")

    strength_progressing: bool = Field(False, description="Whether strength is increasing")
    strength_trends: dict = Field(default_factory=dict, description="Per-exercise strength trends")

    sufficient_data: bool = Field(False, description="Whether enough sessions for analysis")


# ============================================================================
# Database Document Models (for DynamoDB)
# ============================================================================

class WeeklyAnalysisDocument(BaseModel):
    """
    Document stored in weekly_analyses DynamoDB table.

    Contains complete analysis results from Nutrition Specialist.
    """
    user_id: str = Field(..., description="User identifier")
    week_starting: str = Field(..., description="ISO date of Monday starting the week")
    status: Literal["completed", "failed", "insufficient_data"] = Field(..., description="Analysis status")

    # Data summary
    data_summary: dict = Field(..., description="Summary of all analyzed data")

    # Issues detected
    issues_detected: list[dict] = Field(default_factory=list, description="List of detected issues")

    # Plan updates
    plan_updated: bool = Field(False, description="Whether nutrition plan was updated")
    updates: dict = Field(default_factory=dict, description="Details of plan updates")

    # Metadata
    analyzed_at: str = Field(..., description="ISO timestamp of analysis")
    analysis_duration_ms: int = Field(..., description="Time taken for analysis (ms)")

    # Optional fields
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ActivePlanDocument(BaseModel):
    """
    Document stored in active_plans DynamoDB table.

    Contains current active nutrition plan for user.
    """
    user_id: str = Field(..., description="User identifier")
    plan_type: Literal["nutrition"] = Field("nutrition", description="Always 'nutrition' for this table")
    version: int = Field(..., ge=1, description="Plan version number")
    created_at: str = Field(..., description="ISO timestamp of creation")
    active: bool = Field(True, description="Whether plan is currently active")

    # Nutrition plan fields
    target_calories: int = Field(..., ge=0, description="Daily calorie target")
    macro_split: MacroSplit = Field(..., description="Macro split")

    # Metadata
    reason_for_update: str = Field(..., description="Why this plan was created")
    previous_version: Optional[int] = Field(None, description="Previous plan version")
    updated_by: str = Field("nutrition_specialist", description="Agent that created this plan")


# ============================================================================
# User Profile Model (Extended)
# ============================================================================

class UserProfile(BaseModel):
    """
    User profile with all fields needed by Nutrition Agent.

    Matches USER_PROFILE_SCHEMA.md specification.
    """
    # Identifiers
    id: str = Field(..., description="Unique profile ID (UUID)")
    user_id: str = Field(..., description="User identifier")

    # Personal information
    name: Optional[str] = Field(None, description="First name for personalization")
    age: Optional[int] = Field(None, ge=10, le=120, description="Age in years")
    sex: Literal["male", "female"] = Field(..., description="Sex (required for Table 1)")
    height_cm: Optional[float] = Field(None, ge=50, le=300, description="Height in cm")

    # Current metrics
    body_weight_kg: float = Field(..., ge=20, le=500, description="Current body weight (kg)")
    body_fat_pct: float = Field(..., ge=3, le=60, description="Current body fat %")

    # Fitness goals
    goal: Literal["lose_weight", "build_muscle", "maintain"] = Field(..., description="Primary fitness goal")
    training_status: Literal["novice", "intermediate", "advanced"] = Field(
        "novice",
        description="Training experience level"
    )

    # Nutrition targets (updated by Nutrition Agent)
    target_calories: int = Field(..., ge=0, description="Daily calorie target")
    target_protein: float = Field(..., ge=0, description="Daily protein target (g)")
    target_carbs: float = Field(..., ge=0, description="Daily carbs target (g)")
    target_fats: float = Field(..., ge=0, description="Daily fats target (g)")

    # Energy calculations
    bmr: Optional[float] = Field(None, description="Basal Metabolic Rate")
    tdee: Optional[float] = Field(None, description="Total Daily Energy Expenditure")
    activity_level: float = Field(1.2, ge=1.0, le=2.5, description="Activity multiplier")

    # Account status
    is_active: bool = Field(True, description="Whether user is active (for weekly analysis)")

    # Communication preferences
    communication_style: Literal["encouraging", "direct", "scientific"] = Field(
        "encouraging",
        description="Preferred communication style"
    )
    language: str = Field("en", description="Language code (ISO 639-1)")
    timezone: str = Field("UTC", description="User timezone")

    # Timestamps
    created_at: str = Field(..., description="Profile creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# ============================================================================
# Training Agent Models
# ============================================================================

class Set(BaseModel):
    """
    A single set in a workout.

    Used to track individual sets and analyze performance.
    """
    weight: float = Field(..., ge=0, description="Weight used (kg)")
    reps: int = Field(..., ge=0, description="Reps completed")


class Session(BaseModel):
    """
    A workout session for a specific exercise.

    Used in session history for progression analysis.
    """
    date: str = Field(..., description="Session date (ISO format)")
    first_set: Set = Field(..., description="First work set (progression benchmark)")


class ExerciseConfig(BaseModel):
    """
    Configuration for an exercise's progression model.

    Stored in user_exercises table.
    """
    progression_model: Literal["linear", "rep_range"] = Field(..., description="Progression model")
    rep_target: int = Field(..., ge=1, le=50, description="Target reps for progression")
    num_sets: int = Field(..., ge=1, le=10, description="Number of sets per session")
    available_increments: list[float] = Field(..., description="Available weight increments (kg)")
    selected_increment: float = Field(..., ge=0, description="Selected increment for this exercise")


class NextSession(BaseModel):
    """
    Prescription for the next workout session.

    Contains weight, reps, and action type.
    """
    weight: float = Field(..., ge=0, description="Prescribed weight (kg)")
    target_reps: int = Field(..., ge=1, description="Target reps")
    action: Literal[
        "increase_weight",
        "add_reps",
        "plateau_breaker",
        "reactive_deload",
        "retry"
    ] = Field(..., description="Action type for next session")
    message: str = Field(..., description="User-facing message")
    reasoning: str = Field(..., description="Why this prescription was made")


class NextSessionRecommendation(BaseModel):
    """
    Complete recommendation output from Training Specialist Agent.

    Includes today's analysis and next session prescription.
    """
    exercise_name: str = Field(..., description="Exercise name")
    progression_model: Literal["linear", "rep_range"] = Field(..., description="Progression model used")

    # Today's analysis
    today_first_set: Set = Field(..., description="Today's first set")
    hit_rep_target: bool = Field(..., description="Whether rep target was hit")
    plateau_detected: bool = Field(False, description="Whether plateau was detected")
    regression_detected: bool = Field(False, description="Whether regression was detected")
    reactive_deload_implemented: bool = Field(False, description="Whether reactive deload was needed")

    # Next session prescription (algorithmic)
    next_weight: float = Field(..., ge=0, description="Next session weight (kg)")
    next_rep_target: int = Field(..., ge=1, description="Next session target reps")
    action_type: Literal[
        "increase_weight",
        "add_reps",
        "plateau_breaker",
        "reactive_deload",
        "retry"
    ] = Field(..., description="Action type")

    # User-facing messages
    message: str = Field(..., description="User-facing summary message")
    reasoning: str = Field(..., description="Technical reasoning")

    # Optional suggestions
    model_switch_suggestion: Optional["ModelSwitchSuggestion"] = Field(
        None,
        description="Suggestion to switch progression models"
    )
    increment_adjustment_suggestion: Optional[float] = Field(
        None,
        description="Suggested new increment"
    )

    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")


class PlateauAnalysis(BaseModel):
    """
    Analysis of plateau detection.

    Used in Rep Range progression to detect lack of progress.
    """
    plateau_detected: bool = Field(..., description="Whether plateau was detected")
    duration_sessions: int = Field(0, description="Number of sessions without progress")
    last_progressed_date: Optional[str] = Field(None, description="Last date of progression")


class ModelSwitchSuggestion(BaseModel):
    """
    Suggestion to switch progression models.

    Provided when increment becomes too large or failure rate too high.
    """
    from_model: Literal["linear", "rep_range"] = Field(..., description="Current model")
    to_model: Literal["linear", "rep_range"] = Field(..., description="Suggested model")
    reason: str = Field(..., description="Why switch is suggested")


# ============================================================================
# Utility Models
# ============================================================================

class AnalysisInput(BaseModel):
    """
    Input data structure for nutrition algorithm.

    Combines user profile with analyzed trends.
    """
    user_profile: dict = Field(..., description="User profile data")
    weight_trend: WeightTrend = Field(..., description="Weight trend analysis")
    body_comp_trend: BodyCompositionTrend = Field(..., description="Body composition trend")
    nutrition_summary: NutritionSummary = Field(..., description="Nutrition summary")
    workout_summary: WorkoutSummary = Field(..., description="Workout summary")


# ============================================================================
# Export all models
# ============================================================================

__all__ = [
    # Nutrition models
    "MacroSplit",
    "NutritionRecommendation",
    "WeightTrend",
    "BodyCompositionTrend",
    "NutritionSummary",
    "WorkoutSummary",
    "WeeklyAnalysisDocument",
    "ActivePlanDocument",
    "UserProfile",
    "AnalysisInput",
    # Training models
    "Set",
    "Session",
    "ExerciseConfig",
    "NextSession",
    "NextSessionRecommendation",
    "PlateauAnalysis",
    "ModelSwitchSuggestion",
]
