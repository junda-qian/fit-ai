'use client';

import { useState } from 'react';
import { Dumbbell, TrendingUp, Activity, Zap, Calendar, Target } from 'lucide-react';

interface WorkoutPlannerInputs {
  training_status: string;
  sex: string;
  recovery_factor: string;
  energy_balance_factor: string;
  age: string;
  training_frequency: string;
  dedication_level: string;
}

interface ExerciseSet {
  exercise_name: string;
  sets: number;
  intensity: number;
  muscle_activation: Record<string, number>;
}

interface WorkoutDay {
  day_name: string;
  frequency_per_week: number;
  exercises: ExerciseSet[];
}

interface WeeklyVolumeSummary {
  muscle_group: string;
  weekly_sets: number;
}

interface WorkoutPlanResults {
  estimated_optimal_sets: number;
  target_volume_range: {
    min: number;
    max: number;
  };
  workout_days: WorkoutDay[];
  weekly_volume_summary: WeeklyVolumeSummary[];
}

export default function WorkoutPlanner() {
  const [inputs, setInputs] = useState<WorkoutPlannerInputs>({
    training_status: '1',
    sex: '0',
    recovery_factor: '1.0',
    energy_balance_factor: '1.0',
    age: '',
    training_frequency: '3',
    dedication_level: 'B',
  });

  const [results, setResults] = useState<WorkoutPlanResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setInputs({
      ...inputs,
      [e.target.name]: e.target.value,
    });
  };

  const generateWorkoutPlan = async () => {
    setLoading(true);
    setError(null);

    try {
      // Convert inputs to appropriate types
      const payload = {
        training_status: parseInt(inputs.training_status),
        sex: parseInt(inputs.sex),
        recovery_factor: parseFloat(inputs.recovery_factor),
        energy_balance_factor: parseFloat(inputs.energy_balance_factor),
        age: parseInt(inputs.age),
        training_frequency: parseInt(inputs.training_frequency),
        dedication_level: inputs.dedication_level,
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/generate-workout-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to generate workout plan');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    generateWorkoutPlan();
  };

  return (
    <div className="space-y-8">
      {/* Input Form */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <Dumbbell className="w-6 h-6 text-purple-600" />
          Your Training Profile
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Training Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Training Status
            </label>
            <select
              name="training_status"
              value={inputs.training_status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            >
              <option value="1">Novice</option>
              <option value="2">Intermediate</option>
              <option value="3">Advanced</option>
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sex */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sex
              </label>
              <select
                name="sex"
                value={inputs.sex}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              >
                <option value="0">Male</option>
                <option value="1">Female</option>
              </select>
            </div>

            {/* Age */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Age
              </label>
              <input
                type="number"
                name="age"
                value={inputs.age}
                onChange={handleInputChange}
                min="10"
                max="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Recovery Factor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recovery Factor (0.5 - 1.2)
              </label>
              <input
                type="number"
                step="0.1"
                name="recovery_factor"
                value={inputs.recovery_factor}
                onChange={handleInputChange}
                min="0.5"
                max="1.2"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Poor recovery: 0.5 | Good: 1.0 | Excellent: 1.2</p>
            </div>

            {/* Energy Balance Factor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Energy Balance Factor
              </label>
              <input
                type="number"
                step="0.1"
                name="energy_balance_factor"
                value={inputs.energy_balance_factor}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Deficit: 0.8 | Maintenance: 1.0 | Surplus: 1.2</p>
            </div>
          </div>

          {/* Training Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Training Frequency (days per week)
            </label>
            <select
              name="training_frequency"
              value={inputs.training_frequency}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            >
              {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                <option key={num} value={num}>
                  {num} {num === 1 ? 'day' : 'days'} per week
                </option>
              ))}
            </select>
          </div>

          {/* Dedication Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dedication Level
            </label>
            <select
              name="dedication_level"
              value={inputs.dedication_level}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            >
              <option value="A">A - Sustainability Focus (60-75% volume)</option>
              <option value="B">B - Balanced Approach (75-90% volume)</option>
              <option value="C">C - Maximum Results (90-100% volume)</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {inputs.dedication_level === 'A' && 'Sustainability is most important. Steady progress over time.'}
              {inputs.dedication_level === 'B' && 'Balance between results and sustainability.'}
              {inputs.dedication_level === 'C' && 'Maximum results without compromising health.'}
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                Generating Your Workout Plan...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Generate Workout Plan
              </>
            )}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
        </form>
      </div>

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-5 h-5 text-purple-600" />
                <h3 className="text-sm font-semibold text-gray-700">Optimal Sets</h3>
              </div>
              <p className="text-3xl font-bold text-purple-900">{results.estimated_optimal_sets}</p>
              <p className="text-xs text-gray-500 mt-1">Per muscle per week</p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <h3 className="text-sm font-semibold text-gray-700">Target Range</h3>
              </div>
              <p className="text-3xl font-bold text-green-900">
                {results.target_volume_range.min} - {results.target_volume_range.max}
              </p>
              <p className="text-xs text-gray-500 mt-1">Sets per muscle per week</p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-semibold text-gray-700">Training Days</h3>
              </div>
              <p className="text-3xl font-bold text-blue-900">{results.workout_days.length}</p>
              <p className="text-xs text-gray-500 mt-1">Different workout types</p>
            </div>
          </div>

          {/* Workout Days */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <Activity className="w-6 h-6 text-purple-600" />
              Your Personalized Workout Plan
            </h2>

            {results.workout_days.map((day, dayIndex) => (
              <div key={dayIndex} className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-800">{day.day_name}</h3>
                  <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                    {day.frequency_per_week}x per week
                  </span>
                </div>

                <div className="space-y-3">
                  {day.exercises.map((exercise, exIndex) => (
                    <div key={exIndex} className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-800">{exercise.exercise_name}</h4>
                          <div className="flex gap-4 mt-2 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <span className="font-medium">Sets:</span> {exercise.sets}
                            </span>
                            <span className="flex items-center gap-1">
                              <span className="font-medium">Intensity:</span> {exercise.intensity}%
                            </span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {Object.entries(exercise.muscle_activation).map(([muscle, value]) => (
                              <span
                                key={muscle}
                                className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                              >
                                {muscle}: {value}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Weekly Volume Summary */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Weekly Volume Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {results.weekly_volume_summary.map((volume, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    volume.weekly_sets >= results.target_volume_range.min &&
                    volume.weekly_sets <= results.target_volume_range.max
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-yellow-50 border border-yellow-200'
                  }`}
                >
                  <p className="text-sm font-medium text-gray-700">{volume.muscle_group}</p>
                  <p className="text-2xl font-bold text-gray-900">{volume.weekly_sets}</p>
                  <p className="text-xs text-gray-500">sets/week</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-4">
              Green = within target range ({results.target_volume_range.min}-{results.target_volume_range.max} sets)
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
