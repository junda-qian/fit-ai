'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, Scale, Flame, Dumbbell, Calendar, ArrowLeft } from 'lucide-react';
import Navigation from '@/components/navigation';
import Link from 'next/link';

interface BodyLog {
  date: string;
  weight: number;
  body_fat_pct: number | null;
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

export default function ProgressPage() {
  const [bodyLogs, setBodyLogs] = useState<BodyLog[]>([]);
  const [dailySummaries, setDailySummaries] = useState<DailySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<'7' | '30' | '90'>('30');

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
          const barHeight = (summary.total_calories / maxCalories) * chartHeight;
          const x = idx * (barWidth + barGap);
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
          const proteinPct = (summary.total_protein / totalMacros) * 100;
          const carbsPct = (summary.total_carbs / totalMacros) * 100;
          const fatsPct = (summary.total_fats / totalMacros) * 100;

          const x = idx * (barWidth + barGap);
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
