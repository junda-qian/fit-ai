"""
Shared utilities for all AI agents

Includes:
- Pydantic models for structured outputs
- Database client interfaces
- Context wrappers
- Common utility functions
"""

from .models import (
    # Core nutrition models
    NutritionRecommendation,
    MacroSplit,
    WeightTrend,
    BodyCompositionTrend,
    NutritionSummary,
    WorkoutSummary,
    # Database documents
    WeeklyAnalysisDocument,
    ActivePlanDocument,
    UserProfile,
    AnalysisInput,
)

__all__ = [
    "NutritionRecommendation",
    "MacroSplit",
    "WeightTrend",
    "BodyCompositionTrend",
    "NutritionSummary",
    "WorkoutSummary",
    "WeeklyAnalysisDocument",
    "ActivePlanDocument",
    "UserProfile",
    "AnalysisInput",
]
