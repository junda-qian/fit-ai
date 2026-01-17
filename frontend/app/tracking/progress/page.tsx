'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, Scale, Flame, Dumbbell, Calendar, ArrowLeft, Sparkles, Activity } from 'lucide-react';
import Navigation from '@/components/navigation';
import Link from 'next/link';

interface BodyLog {
  date: string;
  weight: number;
  body_fat_pct: number | null;
  skinfold_sum: number | null;
  skinfolds: Record<string, number> | null;
}

interface DailySummary {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fats: number;
  workouts_completed: number;
  weight: number | null;
  targets?: {
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
  };
}

interface NutritionRecommendation {
  current_calorie_average: number;
  recommended_calories: number;
  recommended_macros: {
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
  adjustment_category: 'increase' | 'decrease' | 'none';
  reasoning: string;
  body_composition_status: string;
  confidence: number;
}

interface TrainingSummary {
  user_id: string;
  week: string;
  overall_strength_trend: 'improving' | 'stable' | 'declining' | 'insufficient_data';
  exercises_analyzed: number;
  exercises_progressing: number;
  exercises_plateaued: number;
  exercises_regressing: number;
  avg_weekly_volume_kg: number;
  data_quality: 'good' | 'fair' | 'poor';
  trend_confidence: number;
}

interface StreakData {
  nutrition_current_streak: number;
  nutrition_longest_streak: number;
  nutrition_last_logged_date: string | null;
  workout_current_streak: number;
  workout_longest_streak: number;
  workout_target_per_week: number;
  workout_this_week_count: number;
  sufficient_data: boolean;
  days_analyzed: number;
}

interface MotivationalMessage {
  message: string;
  tone: string;
  highlights: string[];
  generated_at: string;
  model_used: string;
}

interface MotivatorResponse {
  user_id: string;
  streaks: StreakData;
  motivation: MotivationalMessage;
  achievements: Array<{ type: string; description: string }>;
  data_quality: 'excellent' | 'good' | 'fair' | 'poor';
}

export default function ProgressPage() {
  const [bodyLogs, setBodyLogs] = useState<BodyLog[]>([]);
  const [dailySummaries, setDailySummaries] = useState<DailySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<'7' | '30' | '90'>('30');
  const [nutritionRecommendation, setNutritionRecommendation] = useState<NutritionRecommendation | null>(null);
  const [loadingRecommendation, setLoadingRecommendation] = useState(false);
  const [trainingSummary, setTrainingSummary] = useState<TrainingSummary | null>(null);
  const [loadingTrainingSummary, setLoadingTrainingSummary] = useState(false);
  const [motivatorData, setMotivatorData] = useState<MotivatorResponse | null>(null);
  const [loadingMotivator, setLoadingMotivator] = useState(false);

  const fetchProgressData = async () => {
    setLoading(true);
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) {
        window.location.href = '/calculator';
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - parseInt(dateRange));

      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];

      // Fetch body logs
      const bodyRes = await fetch(
        `${apiUrl}/api/body/logs?user_id=${userId}&start_date=${startDateStr}&end_date=${endDateStr}`
      );
      if (bodyRes.ok) {
        const bodyData = await bodyRes.json();
        setBodyLogs(bodyData.reverse()); // Oldest first for charts
      }

      // Fetch daily summaries
      const summaryRes = await fetch(
        `${apiUrl}/api/summary/range?user_id=${userId}&start_date=${startDateStr}&end_date=${endDateStr}`
      );
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setDailySummaries(summaryData.reverse()); // Oldest first for charts
      }

    } catch (err) {
      console.error('Error fetching progress data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProgressData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dateRange]);

  useEffect(() => {
    const userId = localStorage.getItem('fit_tracker_user_id');
    if (userId) {
      fetchMotivatorData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchNutritionRecommendation = async () => {
    setLoadingRecommendation(true);
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) return;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/nutrition/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });

      if (response.ok) {
        const data = await response.json();
        setNutritionRecommendation(data.recommendation);
      }
    } catch (err) {
      console.error('Error fetching nutrition recommendation:', err);
    } finally {
      setLoadingRecommendation(false);
    }
  };

  const fetchTrainingSummary = async () => {
    setLoadingTrainingSummary(true);
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) return;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/training/weekly-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });

      if (response.ok) {
        const data = await response.json();
        setTrainingSummary(data.summary);
      }
    } catch (err) {
      console.error('Error fetching training summary:', err);
    } finally {
      setLoadingTrainingSummary(false);
    }
  };

  const fetchMotivatorData = async () => {
    setLoadingMotivator(true);
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) return;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/motivator/status?user_id=${userId}`);

      if (response.ok) {
        const data = await response.json();
        setMotivatorData(data);
      }
    } catch (err) {
      console.error('Error fetching motivator data:', err);
    } finally {
      setLoadingMotivator(false);
    }
  };

  const calculateWeightStats = () => {
    if (bodyLogs.length === 0) return null;
    const weights = bodyLogs.map(log => log.weight);
    const latest = weights[weights.length - 1];
    const earliest = weights[0];
    const change = latest - earliest;
    const avg = weights.reduce((a, b) => a + b, 0) / weights.length;

    return {
      current: latest,
      change: change,
      avg: avg,
      min: Math.min(...weights),
      max: Math.max(...weights),
    };
  };

  const calculateNutritionStats = () => {
    if (dailySummaries.length === 0) return null;

    const summariesWithTargets = dailySummaries.filter(s => s.targets);
    if (summariesWithTargets.length === 0) return null;

    const avgCalories = summariesWithTargets.reduce((a, b) => a + b.total_calories, 0) / summariesWithTargets.length;
    const avgProtein = summariesWithTargets.reduce((a, b) => a + b.total_protein, 0) / summariesWithTargets.length;
    const targetCalories = summariesWithTargets[0].targets!.calories;
    const targetProtein = summariesWithTargets[0].targets!.protein;

    return {
      avgCalories: Math.round(avgCalories),
      avgProtein: Math.round(avgProtein),
      targetCalories,
      targetProtein,
      caloriesAdherence: Math.round((avgCalories / targetCalories) * 100),
      proteinAdherence: Math.round((avgProtein / targetProtein) * 100),
    };
  };

  const calculateWorkoutStats = () => {
    const totalWorkouts = dailySummaries.reduce((a, b) => a + (b.workouts_completed || 0), 0);
    const daysWithWorkouts = dailySummaries.filter(s => s.workouts_completed > 0).length;
    const avgPerWeek = (totalWorkouts / parseInt(dateRange)) * 7;

    return {
      total: totalWorkouts,
      daysActive: daysWithWorkouts,
      avgPerWeek: avgPerWeek.toFixed(1),
    };
  };

  const weightStats = calculateWeightStats();
  const nutritionStats = calculateNutritionStats();
  const workoutStats = calculateWorkoutStats();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Navigation />

      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <Link href="/tracking/dashboard" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            Progress Tracking
          </h1>
          <p className="text-gray-600">Visualize your fitness journey over time</p>
        </div>

        {/* Date Range Selector */}
        <div className="bg-white rounded-xl shadow-lg p-4 mb-8">
          <div className="flex items-center gap-2 flex-wrap">
            <Calendar className="w-5 h-5 text-gray-600" />
            <span className="text-gray-700 font-medium">Time Range:</span>
            <div className="flex gap-2">
              {(['7', '30', '90'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    dateRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {range} days
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Summary Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Weight Stats */}
          {weightStats && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <Scale className="w-6 h-6 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-800">Weight Progress</h2>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Current:</span>
                  <span className="font-bold text-gray-800">{weightStats.current.toFixed(1)} kg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Change:</span>
                  <span className={`font-bold ${weightStats.change >= 0 ? 'text-blue-600' : 'text-green-600'}`}>
                    {weightStats.change >= 0 ? '+' : ''}{weightStats.change.toFixed(1)} kg
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Average:</span>
                  <span className="font-semibold text-gray-700">{weightStats.avg.toFixed(1)} kg</span>
                </div>
              </div>
            </div>
          )}

          {/* Nutrition Stats */}
          {nutritionStats && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <Flame className="w-6 h-6 text-orange-600" />
                <h2 className="text-xl font-bold text-gray-800">Nutrition</h2>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Calories:</span>
                  <span className="font-bold text-gray-800">{nutritionStats.avgCalories}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Target:</span>
                  <span className="font-semibold text-gray-700">{nutritionStats.targetCalories}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Adherence:</span>
                  <span className={`font-bold ${Math.abs(nutritionStats.caloriesAdherence - 100) <= 10 ? 'text-green-600' : 'text-orange-600'}`}>
                    {nutritionStats.caloriesAdherence}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Workout Stats */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Dumbbell className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-800">Workouts</h2>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Total:</span>
                <span className="font-bold text-gray-800">{workoutStats.total}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Active Days:</span>
                <span className="font-semibold text-gray-700">{workoutStats.daysActive}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Per Week:</span>
                <span className="font-bold text-blue-600">{workoutStats.avgPerWeek}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Evidence-Based Nutrition Recommendation */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl shadow-lg p-6 mb-8 border-2 border-purple-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold text-gray-800">Evidence-Based Nutrition Analysis</h2>
            </div>
            <button
              onClick={fetchNutritionRecommendation}
              disabled={loadingRecommendation}
              className="bg-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-purple-700 disabled:bg-purple-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {loadingRecommendation ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Get Recommendation
                </>
              )}
            </button>
          </div>

          {nutritionRecommendation ? (
            <div className="space-y-4">
              {/* Status Badge */}
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-4 py-2 rounded-full font-medium ${
                  nutritionRecommendation.adjustment_category === 'decrease'
                    ? 'bg-orange-100 text-orange-700'
                    : nutritionRecommendation.adjustment_category === 'increase'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-green-100 text-green-700'
                }`}>
                  {nutritionRecommendation.adjustment_category === 'decrease' && '📉 Decrease Calories'}
                  {nutritionRecommendation.adjustment_category === 'increase' && '📈 Increase Calories'}
                  {nutritionRecommendation.adjustment_category === 'none' && '✅ Maintain Current Plan'}
                </span>
                <span className="px-4 py-2 rounded-full bg-purple-100 text-purple-700 font-medium">
                  {nutritionRecommendation.body_composition_status === 'fat_loss' && '🔥 Fat Loss'}
                  {nutritionRecommendation.body_composition_status === 'muscle_gain' && '💪 Muscle Gain'}
                  {nutritionRecommendation.body_composition_status === 'recomp' && '⚡ Body Recomposition'}
                  {nutritionRecommendation.body_composition_status === 'maintenance' && '🎯 Maintenance'}
                </span>
              </div>

              {/* Calorie Recommendation */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-3">Calorie Recommendation</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Current Average</span>
                    <div className="text-2xl font-bold text-gray-800">{nutritionRecommendation.current_calorie_average} cal/day</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Recommended</span>
                    <div className={`text-2xl font-bold ${
                      nutritionRecommendation.adjustment_category === 'decrease'
                        ? 'text-orange-600'
                        : nutritionRecommendation.adjustment_category === 'increase'
                        ? 'text-blue-600'
                        : 'text-green-600'
                    }`}>
                      {nutritionRecommendation.recommended_calories} cal/day
                    </div>
                  </div>
                </div>
              </div>

              {/* Macro Recommendation */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-3">Recommended Macros</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Protein</div>
                    <div className="text-xl font-bold text-red-600">{nutritionRecommendation.recommended_macros.protein_g}g</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Carbs</div>
                    <div className="text-xl font-bold text-green-600">{nutritionRecommendation.recommended_macros.carbs_g}g</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Fats</div>
                    <div className="text-xl font-bold text-yellow-600">{nutritionRecommendation.recommended_macros.fat_g}g</div>
                  </div>
                </div>
              </div>

              {/* Reasoning */}
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <h3 className="font-bold text-purple-900 mb-2">Analysis</h3>
                <p className="text-purple-800">{nutritionRecommendation.reasoning}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600">
              <p className="mb-2">Click the button above to get personalized nutrition recommendations based on your last 14 days of data.</p>
              <p className="text-sm text-gray-500">Uses a deterministic algorithm that analyzes your weight trend, body composition, nutrition compliance, and workout frequency to provide research-backed guidance.</p>
            </div>
          )}
        </div>

        {/* Training Progress Analysis */}
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl shadow-lg p-6 mb-8 border-2 border-green-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-6 h-6 text-green-600" />
              <h2 className="text-xl font-bold text-gray-800">Training Progress Analysis</h2>
            </div>
            <button
              onClick={fetchTrainingSummary}
              disabled={loadingTrainingSummary}
              className="bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700 disabled:bg-green-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {loadingTrainingSummary ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Activity className="w-4 h-4" />
                  Generate Weekly Summary
                </>
              )}
            </button>
          </div>

          {trainingSummary ? (
            <div className="space-y-4">
              {/* Status Badge */}
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-4 py-2 rounded-full font-medium ${
                  trainingSummary.overall_strength_trend === 'improving'
                    ? 'bg-green-100 text-green-700'
                    : trainingSummary.overall_strength_trend === 'declining'
                    ? 'bg-red-100 text-red-700'
                    : trainingSummary.overall_strength_trend === 'stable'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {trainingSummary.overall_strength_trend === 'improving' && '📈 Strength Improving'}
                  {trainingSummary.overall_strength_trend === 'declining' && '📉 Strength Declining'}
                  {trainingSummary.overall_strength_trend === 'stable' && '➡️ Strength Stable'}
                  {trainingSummary.overall_strength_trend === 'insufficient_data' && 'ℹ️ Insufficient Data'}
                </span>
                <span className="px-4 py-2 rounded-full bg-teal-100 text-teal-700 font-medium">
                  Week {trainingSummary.week}
                </span>
                <span className={`px-4 py-2 rounded-full font-medium ${
                  trainingSummary.data_quality === 'good'
                    ? 'bg-blue-100 text-blue-700'
                    : trainingSummary.data_quality === 'fair'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  Data Quality: {trainingSummary.data_quality}
                </span>
              </div>

              {/* Exercise Breakdown */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-3">Exercise Breakdown (Last 14 Days)</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Total Analyzed</div>
                    <div className="text-2xl font-bold text-gray-800">{trainingSummary.exercises_analyzed}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Progressing</div>
                    <div className="text-2xl font-bold text-green-600">{trainingSummary.exercises_progressing}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Plateaued</div>
                    <div className="text-2xl font-bold text-yellow-600">{trainingSummary.exercises_plateaued}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Regressing</div>
                    <div className="text-2xl font-bold text-red-600">{trainingSummary.exercises_regressing}</div>
                  </div>
                </div>
              </div>

              {/* Volume Stats */}
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-3">Training Volume</h3>
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-sm text-gray-600">Weekly Volume</span>
                    <div className="text-2xl font-bold text-blue-600">
                      {trainingSummary.avg_weekly_volume_kg?.toFixed(0) || '0'} kg
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Confidence</span>
                    <div className="text-2xl font-bold text-purple-600">
                      {((trainingSummary.trend_confidence || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Interpretation */}
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <h3 className="font-bold text-green-900 mb-2">Analysis</h3>
                <p className="text-green-800">
                  {trainingSummary.overall_strength_trend === 'improving' &&
                    `You're making great progress! ${trainingSummary.exercises_progressing} out of ${trainingSummary.exercises_analyzed} exercises are improving. Keep up the good work!`}
                  {trainingSummary.overall_strength_trend === 'stable' &&
                    `Your strength is maintaining. Consider adjusting your training program if you want to see more progress.`}
                  {trainingSummary.overall_strength_trend === 'declining' &&
                    `${trainingSummary.exercises_regressing} exercises are regressing. This could indicate overtraining, inadequate recovery, or nutrition issues. Consider a deload week.`}
                  {trainingSummary.overall_strength_trend === 'insufficient_data' &&
                    'Not enough training data to assess trends. Log at least 2 weeks of workouts for accurate analysis.'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600">
              <p className="mb-2">Click the button above to analyze your strength progress over the last 14 days.</p>
              <p className="text-sm text-gray-500">Uses a deterministic algorithm that analyzes your workout performance to identify progressing, plateaued, and regressing exercises.</p>
            </div>
          )}
        </div>

        {/* Motivation & Streaks Section */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg p-6 mb-8 border border-purple-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-purple-600" />
              Your Momentum
            </h2>
            <button
              onClick={fetchMotivatorData}
              disabled={loadingMotivator}
              className="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loadingMotivator ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {motivatorData ? (
            <>
              {/* Streaks Display */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {/* Nutrition Streak */}
                <div className="bg-white rounded-lg p-5 shadow-sm border border-orange-100">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl">🔥</span>
                    <span className="text-sm font-medium text-gray-600">Nutrition Logging</span>
                  </div>
                  <div className="text-4xl font-bold text-orange-600 mb-1">
                    {motivatorData.streaks.nutrition_current_streak}
                  </div>
                  <div className="text-xs text-gray-500">
                    day streak • Best: {motivatorData.streaks.nutrition_longest_streak}
                  </div>
                </div>

                {/* Workout Streak */}
                <div className="bg-white rounded-lg p-5 shadow-sm border border-blue-100">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl">💪</span>
                    <span className="text-sm font-medium text-gray-600">Workout Consistency</span>
                  </div>
                  <div className="text-4xl font-bold text-blue-600 mb-1">
                    {motivatorData.streaks.workout_current_streak}
                  </div>
                  <div className="text-xs text-gray-500">
                    week streak • This week: {motivatorData.streaks.workout_this_week_count}/{motivatorData.streaks.workout_target_per_week || 0}
                  </div>
                </div>
              </div>

              {/* Activity Calendars Side-by-Side */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                {/* Nutrition Logging Calendar */}
                <div className="bg-white rounded-lg p-5 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">🔥</span>
                    <h3 className="text-sm font-medium text-gray-700">Nutrition Logging</h3>
                  </div>

                {(() => {
                  // Calculate weeks to show (last 12 weeks)
                  const weeks: Date[][] = [];
                  const today = new Date();
                  const startDate = new Date(today);
                  startDate.setDate(today.getDate() - 83); // ~12 weeks back

                  // Find the Sunday before startDate
                  const dayOfWeek = startDate.getDay();
                  startDate.setDate(startDate.getDate() - dayOfWeek);

                  // Build weeks array
                  let currentDate = new Date(startDate);
                  while (currentDate <= today) {
                    const week: Date[] = [];
                    for (let i = 0; i < 7; i++) {
                      week.push(new Date(currentDate));
                      currentDate.setDate(currentDate.getDate() + 1);
                    }
                    weeks.push(week);
                  }

                  // Get month labels
                  const monthLabels: { month: string; weekIndex: number }[] = [];
                  weeks.forEach((week, weekIndex) => {
                    const firstDay = week[0];
                    if (weekIndex === 0 || firstDay.getDate() <= 7) {
                      monthLabels.push({
                        month: firstDay.toLocaleDateString('en-US', { month: 'short' }),
                        weekIndex
                      });
                    }
                  });

                  return (
                    <div className="overflow-x-auto">
                      <div className="inline-block min-w-full">
                        {/* Month labels */}
                        <div className="flex mb-1" style={{ marginLeft: '28px' }}>
                          {monthLabels.map((label, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-gray-500 font-medium"
                              style={{
                                marginLeft: idx === 0 ? 0 : `${(label.weekIndex - (monthLabels[idx - 1]?.weekIndex || 0)) * 14}px`,
                              }}
                            >
                              {label.month}
                            </div>
                          ))}
                        </div>

                        {/* Calendar grid */}
                        <div className="flex gap-1">
                          {/* Day labels */}
                          <div className="flex flex-col gap-1 pr-2">
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Sun</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Mon</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Tue</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Wed</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Thu</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Fri</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Sat</div>
                          </div>

                          {/* Weeks (columns) */}
                          {weeks.map((week, weekIdx) => (
                            <div key={weekIdx} className="flex flex-col gap-1">
                              {week.map((day, dayIdx) => {
                                const dateStr = day.toISOString().split('T')[0];
                                const isFuture = day > today;

                                // Check if this date has nutrition log
                                const hasNutritionLog = dailySummaries.some(s => s.date === dateStr && s.total_calories > 0);

                                let bgColor = 'bg-gray-100';
                                let title = 'No nutrition logged';

                                if (isFuture) {
                                  bgColor = 'bg-gray-50 border border-gray-200';
                                  title = 'Future date';
                                } else if (hasNutritionLog) {
                                  bgColor = 'bg-orange-500';
                                  title = 'Nutrition logged';
                                }

                                return (
                                  <div
                                    key={dayIdx}
                                    className={`w-3 h-3 rounded-sm ${bgColor} hover:ring-2 hover:ring-orange-400 transition-all cursor-pointer`}
                                    title={`${day.toLocaleDateString('en-US', {
                                      month: 'short',
                                      day: 'numeric',
                                      year: 'numeric'
                                    })}: ${title}`}
                                  />
                                );
                              })}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}

                  {/* Legend */}
                  <div className="flex items-center gap-3 mt-4 text-xs text-gray-500">
                    <span className="text-gray-600 font-medium">Less</span>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-sm bg-gray-100"></div>
                      <span>None</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-sm bg-orange-500"></div>
                      <span>Logged</span>
                    </div>
                    <span className="text-gray-600 font-medium">More</span>
                  </div>
                </div>

                {/* Workout Consistency Calendar */}
                <div className="bg-white rounded-lg p-5 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">💪</span>
                    <h3 className="text-sm font-medium text-gray-700">Workout Consistency</h3>
                  </div>

                {(() => {
                  // Calculate weeks to show (last 12 weeks)
                  const weeks: Date[][] = [];
                  const today = new Date();
                  const startDate = new Date(today);
                  startDate.setDate(today.getDate() - 83); // ~12 weeks back

                  // Find the Sunday before startDate
                  const dayOfWeek = startDate.getDay();
                  startDate.setDate(startDate.getDate() - dayOfWeek);

                  // Build weeks array
                  let currentDate = new Date(startDate);
                  while (currentDate <= today) {
                    const week: Date[] = [];
                    for (let i = 0; i < 7; i++) {
                      week.push(new Date(currentDate));
                      currentDate.setDate(currentDate.getDate() + 1);
                    }
                    weeks.push(week);
                  }

                  // Get month labels
                  const monthLabels: { month: string; weekIndex: number }[] = [];
                  weeks.forEach((week, weekIndex) => {
                    const firstDay = week[0];
                    if (weekIndex === 0 || firstDay.getDate() <= 7) {
                      monthLabels.push({
                        month: firstDay.toLocaleDateString('en-US', { month: 'short' }),
                        weekIndex
                      });
                    }
                  });

                  return (
                    <div className="overflow-x-auto">
                      <div className="inline-block min-w-full">
                        {/* Month labels */}
                        <div className="flex mb-1" style={{ marginLeft: '28px' }}>
                          {monthLabels.map((label, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-gray-500 font-medium"
                              style={{
                                marginLeft: idx === 0 ? 0 : `${(label.weekIndex - (monthLabels[idx - 1]?.weekIndex || 0)) * 14}px`,
                              }}
                            >
                              {label.month}
                            </div>
                          ))}
                        </div>

                        {/* Calendar grid */}
                        <div className="flex gap-1">
                          {/* Day labels */}
                          <div className="flex flex-col gap-1 pr-2">
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Sun</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Mon</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Tue</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Wed</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Thu</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Fri</div>
                            <div className="h-3 text-xs text-gray-400" style={{ lineHeight: '12px' }}>Sat</div>
                          </div>

                          {/* Weeks (columns) */}
                          {weeks.map((week, weekIdx) => (
                            <div key={weekIdx} className="flex flex-col gap-1">
                              {week.map((day, dayIdx) => {
                                const dateStr = day.toISOString().split('T')[0];
                                const isFuture = day > today;

                                // Check if this date has workout log
                                const hasWorkoutLog = dailySummaries.some(s => s.date === dateStr && s.workouts_completed > 0);

                                let bgColor = 'bg-gray-100';
                                let title = 'No workout';

                                if (isFuture) {
                                  bgColor = 'bg-gray-50 border border-gray-200';
                                  title = 'Future date';
                                } else if (hasWorkoutLog) {
                                  bgColor = 'bg-blue-500';
                                  title = 'Workout completed';
                                }

                                return (
                                  <div
                                    key={dayIdx}
                                    className={`w-3 h-3 rounded-sm ${bgColor} hover:ring-2 hover:ring-blue-400 transition-all cursor-pointer`}
                                    title={`${day.toLocaleDateString('en-US', {
                                      month: 'short',
                                      day: 'numeric',
                                      year: 'numeric'
                                    })}: ${title}`}
                                  />
                                );
                              })}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}

                  {/* Legend */}
                  <div className="flex items-center gap-3 mt-4 text-xs text-gray-500">
                    <span className="text-gray-600 font-medium">Less</span>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-sm bg-gray-100"></div>
                      <span>None</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded-sm bg-blue-500"></div>
                      <span>Completed</span>
                    </div>
                    <span className="text-gray-600 font-medium">More</span>
                  </div>
                </div>
              </div>

              {/* AI Motivational Message */}
              <div className="bg-white rounded-lg p-5 shadow-sm mb-4">
                <div className="flex items-start gap-4">
                  <div className="text-4xl flex-shrink-0">🤖</div>
                  <div className="flex-1">
                    <p className="text-gray-800 leading-relaxed text-base">
                      {motivatorData.motivation.message}
                    </p>
                    <p className="text-xs text-gray-400 mt-3">
                      Generated {new Date(motivatorData.motivation.generated_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Achievements */}
              {motivatorData.achievements && motivatorData.achievements.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {motivatorData.achievements.map((achievement, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full border border-yellow-200"
                    >
                      ✨ {achievement.description}
                    </span>
                  ))}
                </div>
              )}

              {/* Data Quality Indicator */}
              <div className="mt-4 text-xs text-gray-500 text-center">
                Data quality: {motivatorData.data_quality}
                {motivatorData.data_quality === 'poor' && ' - Log more days for better insights'}
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-600">
              <p className="mb-2">Track your consistency and stay motivated!</p>
              <p className="text-sm text-gray-500">Start logging nutrition and workouts to build your streaks.</p>
            </div>
          )}
        </div>

        {/* Weight Chart */}
        {bodyLogs.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <Scale className="w-6 h-6 text-purple-600" />
              Weight Trend
            </h2>
            <div className="relative" style={{ height: '300px' }}>
              <WeightChart data={bodyLogs} />
            </div>
          </div>
        )}

        {/* Skinfold Chart */}
        {bodyLogs.filter(log => log.skinfold_sum !== null).length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-teal-600" />
              Body Composition (Skinfolds)
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Skinfold sum (7 sites) - Lower values indicate reduced body fat
            </p>
            <div className="relative" style={{ height: '300px' }}>
              <SkinfoldChart data={bodyLogs} />
            </div>
          </div>
        )}

        {/* Nutrition Chart */}
        {dailySummaries.length > 0 && dailySummaries.some(s => s.targets) && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <Flame className="w-6 h-6 text-orange-600" />
              Daily Calories
            </h2>
            <div className="relative" style={{ height: '300px' }}>
              <CaloriesChart data={dailySummaries} />
            </div>
          </div>
        )}

        {/* Macros Chart */}
        {dailySummaries.length > 0 && dailySummaries.some(s => s.targets) && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-green-600" />
              Macronutrient Breakdown
            </h2>
            <div className="relative" style={{ height: '300px' }}>
              <MacrosChart data={dailySummaries} />
            </div>
          </div>
        )}

        {/* Workout Frequency Chart */}
        {dailySummaries.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <Dumbbell className="w-6 h-6 text-blue-600" />
              Workout Frequency
            </h2>
            <div className="relative" style={{ height: '300px' }}>
              <WorkoutChart data={dailySummaries} />
            </div>
          </div>
        )}

        {/* No Data Message */}
        {bodyLogs.length === 0 && dailySummaries.length === 0 && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-xl font-bold text-gray-800 mb-2">No Progress Data Yet</h3>
            <p className="text-gray-600 mb-6">Start tracking your nutrition, workouts, and weight to see your progress here.</p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Link href="/tracking/nutrition" className="bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700">
                Log Nutrition
              </Link>
              <Link href="/tracking/workouts" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                Log Workout
              </Link>
              <Link href="/tracking/weight" className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700">
                Log Weight
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Simple SVG-based Weight Chart Component
function WeightChart({ data }: { data: BodyLog[] }) {
  if (data.length === 0) return null;

  const weights = data.map(d => d.weight);
  const minWeight = Math.min(...weights);
  const maxWeight = Math.max(...weights);
  const range = maxWeight - minWeight || 1;
  const padding = range * 0.1;

  const chartHeight = 250;
  const chartWidth = 100; // percentage

  const points = data.map((log, idx) => {
    const x = data.length === 1 ? chartWidth / 2 : (idx / (data.length - 1)) * chartWidth;
    const y = chartHeight - ((log.weight - minWeight + padding) / (range + 2 * padding)) * chartHeight;
    return { x, y, date: log.date, weight: log.weight };
  });

  const pathData = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  return (
    <div className="w-full h-full relative">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full" preserveAspectRatio="none">
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map(pct => (
          <line
            key={pct}
            x1="0"
            y1={chartHeight * (pct / 100)}
            x2={chartWidth}
            y2={chartHeight * (pct / 100)}
            stroke="#e5e7eb"
            strokeWidth="0.5"
            vectorEffect="non-scaling-stroke"
          />
        ))}

        {/* Line */}
        <path
          d={pathData}
          fill="none"
          stroke="#9333ea"
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>

      {/* Points as HTML elements - perfectly circular */}
      {points.map((p, idx) => (
        <div
          key={idx}
          className="absolute w-3 h-3 rounded-full bg-purple-600 border-2 border-white shadow-sm cursor-pointer"
          style={{
            left: `${p.x}%`,
            top: `${(p.y / chartHeight) * 100}%`,
            transform: 'translate(-50%, -50%)',
          }}
          title={`${p.date}: ${p.weight} kg`}
        />
      ))}

      {/* X-axis labels */}
      <div className="flex justify-between text-xs text-gray-600 mt-2">
        <span>{new Date(data[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        <span>{new Date(data[data.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      </div>

      {/* Y-axis labels */}
      <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-xs text-gray-600 -ml-12">
        <span>{(minWeight + range + padding).toFixed(1)} kg</span>
        <span>{(minWeight + padding).toFixed(1)} kg</span>
      </div>
    </div>
  );
}

// Calories Chart Component
function CaloriesChart({ data }: { data: DailySummary[] }) {
  const summariesWithTargets = data.filter(s => s.targets);
  if (summariesWithTargets.length === 0) return null;

  const target = summariesWithTargets[0].targets!.calories;
  const calories = summariesWithTargets.map(s => s.total_calories);
  const maxCalories = Math.max(...calories, target) * 1.1; // Add 10% headroom

  const chartHeight = 250;
  const chartWidth = summariesWithTargets.length * 20; // Dynamic width based on number of bars
  const barWidth = 15; // Fixed bar width
  const barGap = 5; // Gap between bars

  return (
    <div className="w-full h-full relative">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full" preserveAspectRatio="none">
        {/* Target line */}
        <line
          x1="0"
          y1={chartHeight - (target / maxCalories) * chartHeight}
          x2={chartWidth}
          y2={chartHeight - (target / maxCalories) * chartHeight}
          stroke="#ef4444"
          strokeWidth="1"
          strokeDasharray="4"
          vectorEffect="non-scaling-stroke"
        />

        {/* Bars */}
        {summariesWithTargets.map((summary, idx) => {
          const x = idx * (barWidth + barGap);

          // Show placeholder for days with no data
          if (summary.total_calories === 0) {
            return (
              <rect
                key={idx}
                x={x}
                y={chartHeight - 10}
                width={barWidth}
                height={10}
                fill="#e5e7eb"
                opacity="0.5"
              >
                <title>{`${summary.date}: No nutrition logged`}</title>
              </rect>
            );
          }

          const barHeight = (summary.total_calories / maxCalories) * chartHeight;
          const isOverTarget = summary.total_calories > target * 1.1;
          const isUnderTarget = summary.total_calories < target * 0.9;
          const color = isOverTarget ? '#ef4444' : isUnderTarget ? '#f59e0b' : '#10b981';

          return (
            <rect
              key={idx}
              x={x}
              y={chartHeight - barHeight}
              width={barWidth}
              height={barHeight}
              fill={color}
              opacity="0.8"
            >
              <title>{`${summary.date}: ${Math.round(summary.total_calories)} cal`}</title>
            </rect>
          );
        })}
      </svg>

      <div className="text-xs text-gray-600 mt-2 flex justify-between">
        <span>{new Date(summariesWithTargets[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        <span className="text-red-600">Target: {target} cal</span>
        <span>{new Date(summariesWithTargets[summariesWithTargets.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      </div>
    </div>
  );
}

// Macros Chart Component
function MacrosChart({ data }: { data: DailySummary[] }) {
  const summariesWithTargets = data.filter(s => s.targets);
  if (summariesWithTargets.length === 0) return null;

  const chartHeight = 250;
  const chartWidth = summariesWithTargets.length * 20; // Dynamic width
  const barWidth = 15; // Fixed bar width
  const barGap = 5; // Gap between bars

  return (
    <div className="w-full h-full relative">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full" preserveAspectRatio="none">
        {summariesWithTargets.map((summary, idx) => {
          const totalMacros = summary.total_protein + summary.total_carbs + summary.total_fats;
          const x = idx * (barWidth + barGap);

          // Skip days with no nutrition data (totalMacros = 0) to avoid NaN
          if (totalMacros === 0) {
            return (
              <g key={idx}>
                {/* Placeholder for days with no data */}
                <rect
                  x={x}
                  y={chartHeight - 10}
                  width={barWidth}
                  height={10}
                  fill="#e5e7eb"
                  opacity="0.5"
                >
                  <title>{`${summary.date} - No nutrition logged`}</title>
                </rect>
              </g>
            );
          }

          const proteinPct = (summary.total_protein / totalMacros) * 100;
          const carbsPct = (summary.total_carbs / totalMacros) * 100;
          const fatsPct = (summary.total_fats / totalMacros) * 100;

          const proteinHeight = (proteinPct / 100) * chartHeight;
          const carbsHeight = (carbsPct / 100) * chartHeight;
          const fatsHeight = (fatsPct / 100) * chartHeight;

          return (
            <g key={idx}>
              {/* Protein (bottom) */}
              <rect
                x={x}
                y={chartHeight - proteinHeight}
                width={barWidth}
                height={proteinHeight}
                fill="#ef4444"
                opacity="0.8"
              >
                <title>{`${summary.date} - Protein: ${Math.round(summary.total_protein)}g`}</title>
              </rect>
              {/* Carbs (middle) */}
              <rect
                x={x}
                y={chartHeight - proteinHeight - carbsHeight}
                width={barWidth}
                height={carbsHeight}
                fill="#10b981"
                opacity="0.8"
              >
                <title>{`${summary.date} - Carbs: ${Math.round(summary.total_carbs)}g`}</title>
              </rect>
              {/* Fats (top) */}
              <rect
                x={x}
                y={chartHeight - proteinHeight - carbsHeight - fatsHeight}
                width={barWidth}
                height={fatsHeight}
                fill="#f59e0b"
                opacity="0.8"
              >
                <title>{`${summary.date} - Fats: ${Math.round(summary.total_fats)}g`}</title>
              </rect>
            </g>
          );
        })}
      </svg>

      <div className="text-xs text-gray-600 mt-2 flex justify-between">
        <span>{new Date(summariesWithTargets[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        <div className="flex gap-4 justify-center">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>Protein</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span>Carbs</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
            <span>Fats</span>
          </div>
        </div>
        <span>{new Date(summariesWithTargets[summariesWithTargets.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      </div>
    </div>
  );
}

// Workout Frequency Chart
function WorkoutChart({ data }: { data: DailySummary[] }) {
  const chartHeight = 250;
  const chartWidth = data.length * 20; // Dynamic width
  const barWidth = 15; // Fixed bar width
  const barGap = 5; // Gap between bars

  return (
    <div className="w-full h-full relative">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full" preserveAspectRatio="none">
        {data.map((summary, idx) => {
          const x = idx * (barWidth + barGap);
          const hasWorkout = summary.workouts_completed > 0;
          const barHeight = hasWorkout ? chartHeight * 0.8 : chartHeight * 0.1;

          return (
            <rect
              key={idx}
              x={x}
              y={chartHeight - barHeight}
              width={barWidth}
              height={barHeight}
              fill={hasWorkout ? '#3b82f6' : '#e5e7eb'}
              opacity="0.8"
            >
              <title>{`${summary.date}: ${summary.workouts_completed} workout${summary.workouts_completed !== 1 ? 's' : ''}`}</title>
            </rect>
          );
        })}
      </svg>

      <div className="text-xs text-gray-600 mt-2 flex justify-between">
        <span>{new Date(data[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        <span>{new Date(data[data.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      </div>
    </div>
  );
}

// Skinfold Sum Chart Component
function SkinfoldChart({ data }: { data: BodyLog[] }) {
  // Filter only logs with skinfold measurements
  const skinfoldLogs = data.filter(log => log.skinfold_sum !== null && log.skinfold_sum > 0);

  if (skinfoldLogs.length === 0) return null;

  const skinfoldSums = skinfoldLogs.map(d => d.skinfold_sum!);
  const minSum = Math.min(...skinfoldSums);
  const maxSum = Math.max(...skinfoldSums);
  const range = maxSum - minSum || 1;
  const padding = range * 0.1;

  const chartHeight = 250;
  const chartWidth = 100; // percentage

  const points = skinfoldLogs.map((log, idx) => {
    const x = skinfoldLogs.length === 1 ? chartWidth / 2 : (idx / (skinfoldLogs.length - 1)) * chartWidth;
    const y = chartHeight - ((log.skinfold_sum! - minSum + padding) / (range + 2 * padding)) * chartHeight;
    return { x, y, date: log.date, sum: log.skinfold_sum! };
  });

  const pathData = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  // Calculate stats
  const startSum = skinfoldSums[0];
  const endSum = skinfoldSums[skinfoldSums.length - 1];
  const totalChange = endSum - startSum;
  const percentChange = ((totalChange / startSum) * 100).toFixed(1);

  return (
    <div className="w-full h-full flex flex-col">
      {/* Stats banner */}
      <div className="bg-teal-50 border border-teal-200 rounded-lg p-3 mb-4 flex justify-between items-center flex-shrink-0">
        <div>
          <span className="text-sm text-teal-700 font-medium">Starting: {startSum.toFixed(1)}mm</span>
        </div>
        <div className="text-center">
          <span className={`text-lg font-bold ${totalChange < 0 ? 'text-green-600' : 'text-orange-600'}`}>
            {totalChange > 0 ? '+' : ''}{totalChange.toFixed(1)}mm ({percentChange}%)
          </span>
          <div className="text-xs text-teal-600">Change over {skinfoldLogs.length} weeks</div>
        </div>
        <div>
          <span className="text-sm text-teal-700 font-medium">Current: {endSum.toFixed(1)}mm</span>
        </div>
      </div>

      {/* Chart container - separate from banner so dots align correctly */}
      <div className="w-full flex-1 relative" style={{ minHeight: '200px' }}>
        <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full" preserveAspectRatio="none">
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map(pct => (
            <line
              key={pct}
              x1="0"
              y1={chartHeight * (pct / 100)}
              x2={chartWidth}
              y2={chartHeight * (pct / 100)}
              stroke="#e5e7eb"
              strokeWidth="0.5"
              vectorEffect="non-scaling-stroke"
            />
          ))}

          {/* Line */}
          <path
            d={pathData}
            fill="none"
            stroke="#14b8a6"
            strokeWidth="2"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        {/* Points as HTML elements */}
        {points.map((p, idx) => (
          <div
            key={idx}
            className="absolute w-3 h-3 rounded-full bg-teal-600 border-2 border-white shadow-sm cursor-pointer"
            style={{
              left: `${p.x}%`,
              top: `${(p.y / chartHeight) * 100}%`,
              transform: 'translate(-50%, -50%)',
            }}
            title={`${p.date}: ${p.sum.toFixed(1)}mm`}
          />
        ))}

        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-xs text-gray-600 -ml-12">
          <span>{(minSum + range + padding).toFixed(1)} mm</span>
          <span>{(minSum + padding).toFixed(1)} mm</span>
        </div>
      </div>

      {/* X-axis labels */}
      <div className="flex justify-between text-xs text-gray-600 mt-2 flex-shrink-0">
        <span>{new Date(skinfoldLogs[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        <span className="text-teal-600 font-medium">{skinfoldLogs.length} weekly measurements</span>
        <span>{new Date(skinfoldLogs[skinfoldLogs.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      </div>
    </div>
  );
}
