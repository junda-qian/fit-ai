'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, Flame, Dumbbell, Scale, Plus } from 'lucide-react';
import Navigation from '@/components/navigation';

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
  progress?: {
    calories_pct: number;
    protein_pct: number;
    carbs_pct: number;
    fats_pct: number;
  };
}

interface WorkoutPlan {
  plan_name: string;
  frequency: string;
  description: string;
}

export default function TrackingDashboard() {
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) {
        window.location.href = '/calculator';
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const today = new Date().toISOString().split('T')[0];

      // Fetch daily summary
      const summaryRes = await fetch(
        `${apiUrl}/api/summary/daily?user_id=${userId}&date=${today}`
      );
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }

      // Fetch active workout plan
      const planRes = await fetch(
        `${apiUrl}/api/workout-plan/${userId}/active`
      );
      if (planRes.ok) {
        const planData = await planRes.json();
        setWorkoutPlan(planData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Navigation />
      <div className="max-w-6xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            Tracking Dashboard
          </h1>
          <p className="text-gray-600">{today}</p>
        </div>

        {/* Today's Progress Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Nutrition Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Flame className="w-6 h-6 text-orange-600" />
              <h2 className="text-xl font-bold text-gray-800">Nutrition</h2>
            </div>

            {summary?.targets ? (
              <>
                <div className="mb-4">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">Calories</span>
                    <span className="text-sm font-semibold text-gray-800">
                      {Math.round(summary.total_calories)} / {summary.targets.calories}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-orange-500 h-3 rounded-full transition-all"
                      style={{ width: `${Math.min(summary.progress?.calories_pct || 0, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1 text-right">{summary.progress?.calories_pct}%</p>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Protein:</span>
                    <span className="font-semibold">{Math.round(summary.total_protein)}g / {summary.targets.protein}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Fats:</span>
                    <span className="font-semibold">{Math.round(summary.total_fats)}g / {summary.targets.fats}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Carbs:</span>
                    <span className="font-semibold">{Math.round(summary.total_carbs)}g / {summary.targets.carbs}g</span>
                  </div>
                </div>

                <a
                  href="/tracking/nutrition"
                  className="w-full mt-4 bg-orange-600 text-white py-2 rounded-lg hover:bg-orange-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Log Meal
                </a>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No targets set</p>
                <a
                  href="/calculator"
                  className="text-blue-600 hover:underline"
                >
                  Complete Energy Calculator →
                </a>
              </div>
            )}
          </div>

          {/* Workout Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Dumbbell className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-800">Workout</h2>
            </div>

            {workoutPlan ? (
              <>
                <div className="mb-4">
                  <p className="text-sm text-gray-600">Active Plan:</p>
                  <p className="font-semibold text-gray-800">{workoutPlan.plan_name}</p>
                  <p className="text-sm text-gray-500">{workoutPlan.frequency}</p>
                </div>

                {summary && summary.workouts_completed > 0 ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                    <p className="text-green-800 font-semibold">✅ Completed today</p>
                  </div>
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
                    <p className="text-gray-600">⏳ Not logged yet</p>
                  </div>
                )}

                <a
                  href="/tracking/workouts"
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Log Workout
                </a>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No active plan</p>
                <a
                  href="/workout-planner"
                  className="text-blue-600 hover:underline"
                >
                  Create Workout Plan →
                </a>
              </div>
            )}
          </div>

          {/* Weight Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Scale className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold text-gray-800">Weight</h2>
            </div>

            {summary?.weight ? (
              <>
                <div className="text-center py-6">
                  <p className="text-4xl font-bold text-gray-800">{summary.weight}</p>
                  <p className="text-gray-600 mt-1">kg</p>
                </div>

                <a
                  href="/tracking/weight"
                  className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Update Weight
                </a>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No weight logged today</p>
                <a
                  href="/tracking/weight"
                  className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Log Weight
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Macro Progress Bars */}
        {summary?.targets && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Today's Macro Breakdown</h2>

            <div className="space-y-4">
              {/* Protein */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Protein</span>
                  <span className="text-sm text-gray-600">{summary.progress?.protein_pct}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-red-500 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min(summary.progress?.protein_pct || 0, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{Math.round(summary.total_protein)}g / {summary.targets.protein}g</p>
              </div>

              {/* Fats */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Fats</span>
                  <span className="text-sm text-gray-600">{summary.progress?.fats_pct}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-yellow-500 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min(summary.progress?.fats_pct || 0, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{Math.round(summary.total_fats)}g / {summary.targets.fats}g</p>
              </div>

              {/* Carbs */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Carbohydrates</span>
                  <span className="text-sm text-gray-600">{summary.progress?.carbs_pct}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-green-500 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min(summary.progress?.carbs_pct || 0, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{Math.round(summary.total_carbs)}g / {summary.targets.carbs}g</p>
              </div>
            </div>
          </div>
        )}

        {/* Quick Stats */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            This Week
          </h2>
          <div className="text-center text-gray-500 py-8">
            Weekly summary coming soon...
          </div>
        </div>
      </div>
    </div>
  );
}
