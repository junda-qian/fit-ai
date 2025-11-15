"""
Trend Analysis Functions

Analyze weight and body composition trends from user logs.
All functions are deterministic and use statistical methods to filter noise.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from statistics import mean
from ..shared.models import WeightTrend, BodyCompositionTrend


# ============================================================================
# Weight Trend Analysis
# ============================================================================

def analyze_weight_trend(weight_logs: List[Dict], days: int = 14) -> WeightTrend:
    """
    Analyze weight trend from body logs.

    Calculates:
    - Average weight
    - Rate of change (daily, weekly, weekly %)
    - Plateau detection
    - Trend direction

    Args:
        weight_logs: List of weight log dictionaries
                     Each should have: {"date": "2025-11-14", "weight": 78.5}
        days: Number of days to analyze (default 14)

    Returns:
        WeightTrend model with analysis results

    Example:
        >>> logs = [
        ...     {"date": "2025-11-01", "weight": 79.0},
        ...     {"date": "2025-11-07", "weight": 78.5},
        ...     {"date": "2025-11-14", "weight": 78.0}
        ... ]
        >>> analyze_weight_trend(logs)
        WeightTrend(
            days_analyzed=14,
            data_points=3,
            starting_weight=79.0,
            current_weight=78.0,
            weekly_rate=-0.5,
            is_plateau=False,
            trend="decreasing"
        )
    """
    # Minimum data requirements
    MIN_DATA_POINTS = 3
    PLATEAU_THRESHOLD_PCT = 0.2  # Less than 0.2%/week = plateau

    # Check if enough data
    if not weight_logs or len(weight_logs) < MIN_DATA_POINTS:
        return WeightTrend(
            days_analyzed=days,
            data_points=len(weight_logs) if weight_logs else 0,
            sufficient_data=False,
            trend="stable"
        )

    # Sort logs by date
    sorted_logs = sorted(weight_logs, key=lambda x: x.get("date", ""))

    # Extract weights
    weights = [log.get("weight") for log in sorted_logs if log.get("weight") is not None]

    if len(weights) < MIN_DATA_POINTS:
        return WeightTrend(
            days_analyzed=days,
            data_points=len(weights),
            sufficient_data=False,
            trend="stable"
        )

    # Calculate metrics
    starting_weight = weights[0]
    current_weight = weights[-1]
    avg_weight = round(mean(weights), 1)
    total_change = round(current_weight - starting_weight, 2)

    # Calculate rates
    # Note: We use 14 days even if logs span different timeframe
    daily_rate = round(total_change / days, 3)
    weekly_rate = round(daily_rate * 7, 2)
    weekly_rate_pct = round((weekly_rate / avg_weight) * 100, 2) if avg_weight > 0 else 0.0

    # Detect plateau
    is_plateau = abs(weekly_rate_pct) < PLATEAU_THRESHOLD_PCT

    # Determine trend
    if abs(weekly_rate_pct) < PLATEAU_THRESHOLD_PCT:
        trend = "stable"
    elif weekly_rate > 0:
        trend = "increasing"
    else:
        trend = "decreasing"

    return WeightTrend(
        days_analyzed=days,
        data_points=len(weights),
        starting_weight=starting_weight,
        current_weight=current_weight,
        avg_weight=avg_weight,
        total_change=total_change,
        daily_rate=daily_rate,
        weekly_rate=weekly_rate,
        weekly_rate_pct=weekly_rate_pct,
        is_plateau=is_plateau,
        trend=trend,
        sufficient_data=True
    )


# ============================================================================
# Body Composition Trend Analysis
# ============================================================================

def analyze_body_composition_trend(
    body_logs: List[Dict],
    days: int = 14
) -> BodyCompositionTrend:
    """
    Analyze body composition trend using multiple methods (prioritized by reliability).

    Priority:
    1. Skinfold measurements (most reliable for trends)
    2. Waist circumference (simple, reliable)
    3. Body fat % estimates (less reliable)
    4. None (insufficient data)

    Args:
        body_logs: List of body log dictionaries
                   Each should have: {"date": "...", "skinfolds": {...}, "waist_cm": ..., "body_fat_pct": ...}
        days: Number of days to analyze (default 14)

    Returns:
        BodyCompositionTrend model with analysis results

    Example:
        >>> logs = [
        ...     {"date": "2025-11-01", "skinfolds": {"tricep": 12, "abdomen": 20, "thigh": 18}, "skinfold_sum": 50},
        ...     {"date": "2025-11-14", "skinfolds": {"tricep": 11, "abdomen": 18, "thigh": 17}, "skinfold_sum": 46}
        ... ]
        >>> analyze_body_composition_trend(logs)
        BodyCompositionTrend(
            method="skinfolds",
            confidence="high",
            starting_skinfold_sum_mm=50,
            current_skinfold_sum_mm=46,
            total_change_mm=-4,
            trend="decreasing"
        )
    """
    MIN_DATA_POINTS = 2
    STABLE_THRESHOLD_MM = 2  # Less than 2mm change = stable (for skinfolds)
    STABLE_THRESHOLD_CM = 1  # Less than 1cm change = stable (for waist)
    STABLE_THRESHOLD_PCT = 1  # Less than 1% change = stable (for BF%)

    # Check if enough data
    if not body_logs or len(body_logs) < MIN_DATA_POINTS:
        return BodyCompositionTrend(
            method="none",
            confidence="none",
            days_analyzed=days,
            data_points=len(body_logs) if body_logs else 0,
            sufficient_data=False,
            trend="stable",
            interpretation="Insufficient data for body composition analysis"
        )

    # Sort logs by date
    sorted_logs = sorted(body_logs, key=lambda x: x.get("date", ""))

    # Try Method 1: Skinfolds (highest priority)
    skinfold_sums = [
        log.get("skinfold_sum")
        for log in sorted_logs
        if log.get("skinfold_sum") is not None
    ]

    if len(skinfold_sums) >= MIN_DATA_POINTS:
        return _analyze_skinfolds(skinfold_sums, days, len(sorted_logs))

    # Try Method 2: Waist circumference
    waist_measurements = [
        log.get("waist_cm")
        for log in sorted_logs
        if log.get("waist_cm") is not None
    ]

    if len(waist_measurements) >= MIN_DATA_POINTS:
        return _analyze_waist(waist_measurements, days, len(sorted_logs))

    # Try Method 3: Body fat percentage
    body_fat_measurements = [
        log.get("body_fat_pct")
        for log in sorted_logs
        if log.get("body_fat_pct") is not None
    ]

    if len(body_fat_measurements) >= MIN_DATA_POINTS:
        return _analyze_body_fat_pct(body_fat_measurements, days, len(sorted_logs))

    # No valid method found
    return BodyCompositionTrend(
        method="none",
        confidence="none",
        days_analyzed=days,
        data_points=len(sorted_logs),
        sufficient_data=False,
        trend="stable",
        interpretation="No body composition measurements found (need skinfolds, waist, or BF%)"
    )


def _analyze_skinfolds(
    skinfold_sums: List[float],
    days: int,
    total_logs: int
) -> BodyCompositionTrend:
    """Analyze skinfold measurements (most reliable method)"""
    STABLE_THRESHOLD = 2  # mm

    starting_sum = skinfold_sums[0]
    current_sum = skinfold_sums[-1]
    total_change = round(current_sum - starting_sum, 1)
    daily_rate = round(total_change / days, 3)

    # Determine stability and trend
    is_stable = abs(total_change) < STABLE_THRESHOLD

    if is_stable:
        trend = "stable"
        interpretation = "Body fat stable"
    elif total_change < 0:
        trend = "decreasing"
        interpretation = "Fat mass decreasing"
    else:
        trend = "increasing"
        interpretation = "Fat mass increasing"

    return BodyCompositionTrend(
        method="skinfolds",
        confidence="high",  # Skinfolds are most reliable for trends
        days_analyzed=days,
        data_points=len(skinfold_sums),
        starting_skinfold_sum_mm=starting_sum,
        current_skinfold_sum_mm=current_sum,
        total_change_mm=total_change,
        daily_rate_mm=daily_rate,
        is_stable=is_stable,
        trend=trend,
        interpretation=interpretation,
        sufficient_data=True
    )


def _analyze_waist(
    waist_measurements: List[float],
    days: int,
    total_logs: int
) -> BodyCompositionTrend:
    """Analyze waist circumference (good alternative method)"""
    STABLE_THRESHOLD = 1  # cm

    starting_waist = waist_measurements[0]
    current_waist = waist_measurements[-1]
    waist_change = round(current_waist - starting_waist, 1)

    # Determine stability and trend
    is_stable = abs(waist_change) < STABLE_THRESHOLD

    if is_stable:
        trend = "stable"
        interpretation = "Waist stable"
    elif waist_change < 0:
        trend = "decreasing"
        interpretation = "Waist decreasing (likely fat loss)"
    else:
        trend = "increasing"
        interpretation = "Waist increasing (likely fat gain)"

    return BodyCompositionTrend(
        method="waist",
        confidence="medium",  # Waist is reliable but less precise than skinfolds
        days_analyzed=days,
        data_points=len(waist_measurements),
        starting_waist_cm=starting_waist,
        current_waist_cm=current_waist,
        waist_change_cm=waist_change,
        is_stable=is_stable,
        trend=trend,
        interpretation=interpretation,
        sufficient_data=True
    )


def _analyze_body_fat_pct(
    body_fat_measurements: List[float],
    days: int,
    total_logs: int
) -> BodyCompositionTrend:
    """Analyze body fat percentage (least reliable method)"""
    STABLE_THRESHOLD = 1  # %

    starting_bf = body_fat_measurements[0]
    current_bf = body_fat_measurements[-1]
    bf_change = round(current_bf - starting_bf, 1)

    # Determine stability and trend
    is_stable = abs(bf_change) < STABLE_THRESHOLD

    if is_stable:
        trend = "stable"
        interpretation = "Body fat % stable (low confidence - consider using skinfolds)"
    elif bf_change < 0:
        trend = "decreasing"
        interpretation = "Body fat % decreasing (low confidence - consider using skinfolds)"
    else:
        trend = "increasing"
        interpretation = "Body fat % increasing (low confidence - consider using skinfolds)"

    return BodyCompositionTrend(
        method="body_fat_pct",
        confidence="low",  # BF% estimates have high error margin
        days_analyzed=days,
        data_points=len(body_fat_measurements),
        starting_body_fat_pct=starting_bf,
        current_body_fat_pct=current_bf,
        body_fat_change_pct=bf_change,
        is_stable=is_stable,
        trend=trend,
        interpretation=interpretation,
        sufficient_data=True
    )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "analyze_weight_trend",
    "analyze_body_composition_trend",
]
