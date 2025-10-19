'use client';

import { useState } from 'react';
import { Calculator, TrendingUp, Activity, Zap } from 'lucide-react';

interface CalculatorInputs {
  bodyweight_kg: string;
  body_fat_percentage: string;
  physical_activity_factor: string;
  thermic_effect_food_factor: string;
  training_duration_min: string;
  energy_balance_factor: string;
  training_days_per_week: string;
}

interface MacroTargets {
  protein_grams: number;
  protein_calories: number;
  fat_grams: number;
  fat_calories: number;
  carbs_grams: number;
  carbs_calories: number;
  protein_percentage: number;
  fat_percentage: number;
  carbs_percentage: number;
}

interface CalculatorResults {
  fat_free_mass_kg: number;
  cunningham_bmr: number;
  training_energy_expenditure: number;
  rest_day_energy_expenditure: number;
  training_day_energy_expenditure: number;
  maintenance_energy_intake: number;
  average_target_energy_intake: number;
  macro_targets: MacroTargets;
}

export default function EnergyCalculator() {
  const [inputs, setInputs] = useState<CalculatorInputs>({
    bodyweight_kg: '',
    body_fat_percentage: '',
    physical_activity_factor: '1.2',
    thermic_effect_food_factor: '1.1',
    training_duration_min: '',
    energy_balance_factor: '1.0',
    training_days_per_week: '4',
  });

  const [results, setResults] = useState<CalculatorResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputs({
      ...inputs,
      [e.target.name]: e.target.value,
    });
  };

  const calculateEnergy = async () => {
    setLoading(true);
    setError(null);

    try {
      // Convert inputs to numbers
      const payload = {
        bodyweight_kg: parseFloat(inputs.bodyweight_kg),
        body_fat_percentage: parseFloat(inputs.body_fat_percentage),
        physical_activity_factor: parseFloat(inputs.physical_activity_factor),
        thermic_effect_food_factor: parseFloat(inputs.thermic_effect_food_factor),
        training_duration_min: parseFloat(inputs.training_duration_min),
        energy_balance_factor: parseFloat(inputs.energy_balance_factor),
        training_days_per_week: parseInt(inputs.training_days_per_week),
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/calculate-energy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to calculate energy metrics');
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
    calculateEnergy();
  };

  // Helper function to generate/get user ID
  const getUserId = (): string => {
    // Check if user ID exists in localStorage
    let userId = localStorage.getItem('fit_tracker_user_id');

    if (!userId) {
      // Generate new user ID: user_timestamp_randomString
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('fit_tracker_user_id', userId);
    }

    return userId;
  };

  // Save profile to backend and navigate to workout planner
  const handleSaveAndContinue = async () => {
    if (!results) return;

    setSaving(true);
    setError(null);

    try {
      const userId = getUserId();

      // Determine goal based on energy balance factor
      let goal = 'maintain';
      const energyFactor = parseFloat(inputs.energy_balance_factor);
      if (energyFactor > 1.0) {
        goal = 'bulk';
      } else if (energyFactor < 1.0) {
        goal = 'cut';
      }

      // Prepare profile data matching backend UserProfileCreate model
      const profileData = {
        user_id: userId,
        target_calories: Math.round(results.average_target_energy_intake),
        target_protein: results.macro_targets.protein_grams,
        target_carbs: results.macro_targets.carbs_grams,
        target_fats: results.macro_targets.fat_grams,
        bmr: results.cunningham_bmr,
        tdee: results.maintenance_energy_intake,
        activity_level: parseFloat(inputs.physical_activity_factor),
        goal: goal,
        body_weight_kg: parseFloat(inputs.bodyweight_kg),
        body_fat_pct: parseFloat(inputs.body_fat_percentage)
      };

      // Save to backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/user-profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        throw new Error('Failed to save profile');
      }

      setSaved(true);

      // Navigate to workout planner after 1 second
      setTimeout(() => {
        window.location.href = '/workout-planner';
      }, 1000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save targets. Please try again.');
      setSaving(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Input Form */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <Calculator className="w-6 h-6 text-blue-600" />
          Input Your Data
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Body Composition */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">Body Composition</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bodyweight (kg)
              </label>
              <input
                type="number"
                step="0.1"
                name="bodyweight_kg"
                value={inputs.bodyweight_kg}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Body Fat Percentage (%)
              </label>
              <input
                type="number"
                step="0.1"
                name="body_fat_percentage"
                value={inputs.body_fat_percentage}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Activity Factors */}
          <div className="space-y-3 pt-4 border-t">
            <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">Activity Factors</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Physical Activity Factor (1.0 - 1.5)
              </label>
              <input
                type="number"
                step="0.1"
                name="physical_activity_factor"
                value={inputs.physical_activity_factor}
                onChange={handleInputChange}
                min="1.0"
                max="1.5"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Sedentary: 1.0 | Moderately Active: 1.2 | Very Active: 1.4</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Thermic Effect of Food Factor (1.0 - 1.25)
              </label>
              <input
                type="number"
                step="0.05"
                name="thermic_effect_food_factor"
                value={inputs.thermic_effect_food_factor}
                onChange={handleInputChange}
                min="1.0"
                max="1.25"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Low protein: 1.0 | High protein: 1.15 | Very high: 1.25</p>
            </div>
          </div>

          {/* Training Schedule */}
          <div className="space-y-3 pt-4 border-t">
            <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">Training Schedule</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Training Duration per Session (minutes)
              </label>
              <input
                type="number"
                step="5"
                name="training_duration_min"
                value={inputs.training_duration_min}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Training Days per Week
              </label>
              <input
                type="number"
                name="training_days_per_week"
                value={inputs.training_days_per_week}
                onChange={handleInputChange}
                min="0"
                max="7"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Energy Balance */}
          <div className="space-y-3 pt-4 border-t">
            <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">Energy Goal</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Energy Balance Factor
              </label>
              <input
                type="number"
                step="0.05"
                name="energy_balance_factor"
                value={inputs.energy_balance_factor}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Deficit: 0.8 (20% cut) | Maintenance: 1.0 | Surplus: 1.1 (10% bulk)
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                Calculating...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Calculate Energy Metrics
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
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-green-600" />
          Your Results
        </h2>

        {!results ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <Activity className="w-16 h-16 mb-4" />
            <p className="text-center">Enter your data and click calculate to see your personalized energy metrics</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-semibold text-blue-800 mb-1">Fat-Free Mass</h3>
              <p className="text-2xl font-bold text-blue-900">{results.fat_free_mass_kg} kg</p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <h3 className="text-sm font-semibold text-purple-800 mb-1">Cunningham BMR</h3>
              <p className="text-2xl font-bold text-purple-900">{results.cunningham_bmr} kcal</p>
              <p className="text-xs text-purple-600 mt-1">Basal Metabolic Rate</p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg">
              <h3 className="text-sm font-semibold text-orange-800 mb-1">Training Energy Expenditure</h3>
              <p className="text-2xl font-bold text-orange-900">{results.training_energy_expenditure} kcal</p>
              <p className="text-xs text-orange-600 mt-1">Per training session</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="text-xs font-semibold text-green-800 mb-1">Rest Day EE</h3>
                <p className="text-xl font-bold text-green-900">{results.rest_day_energy_expenditure} kcal</p>
              </div>

              <div className="p-4 bg-teal-50 rounded-lg">
                <h3 className="text-xs font-semibold text-teal-800 mb-1">Training Day EE</h3>
                <p className="text-xl font-bold text-teal-900">{results.training_day_energy_expenditure} kcal</p>
              </div>
            </div>

            <div className="p-4 bg-indigo-50 rounded-lg border-2 border-indigo-200">
              <h3 className="text-sm font-semibold text-indigo-800 mb-1">Maintenance Energy Intake</h3>
              <p className="text-2xl font-bold text-indigo-900">{results.maintenance_energy_intake} kcal/day</p>
              <p className="text-xs text-indigo-600 mt-1">Weekly average to maintain weight</p>
            </div>

            <div className="p-5 bg-gradient-to-r from-green-400 to-blue-500 rounded-lg text-white">
              <h3 className="text-sm font-semibold mb-1">🎯 Target Energy Intake</h3>
              <p className="text-3xl font-bold">{results.average_target_energy_intake} kcal/day</p>
              <p className="text-xs mt-1 opacity-90">Based on your energy balance goal</p>
            </div>

            {/* Macro Targets Section */}
            <div className="pt-4 border-t-2 border-gray-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                🥗 Macro Nutrient Targets
              </h3>

              {/* Macro Breakdown Cards */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                {/* Protein */}
                <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <h4 className="text-xs font-semibold text-red-800 mb-2">🥩 Protein</h4>
                  <p className="text-2xl font-bold text-red-900">{results.macro_targets.protein_grams}g</p>
                  <p className="text-xs text-red-700 mt-1">{results.macro_targets.protein_calories} kcal</p>
                  <p className="text-xs font-semibold text-red-600 mt-1">{results.macro_targets.protein_percentage}%</p>
                </div>

                {/* Fat */}
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <h4 className="text-xs font-semibold text-yellow-800 mb-2">🥑 Fat</h4>
                  <p className="text-2xl font-bold text-yellow-900">{results.macro_targets.fat_grams}g</p>
                  <p className="text-xs text-yellow-700 mt-1">{results.macro_targets.fat_calories} kcal</p>
                  <p className="text-xs font-semibold text-yellow-600 mt-1">{results.macro_targets.fat_percentage}%</p>
                </div>

                {/* Carbs */}
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <h4 className="text-xs font-semibold text-green-800 mb-2">🍚 Carbs</h4>
                  <p className="text-2xl font-bold text-green-900">{results.macro_targets.carbs_grams}g</p>
                  <p className="text-xs text-green-700 mt-1">{results.macro_targets.carbs_calories} kcal</p>
                  <p className="text-xs font-semibold text-green-600 mt-1">{results.macro_targets.carbs_percentage}%</p>
                </div>
              </div>

              {/* Pie Chart Visualization */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 text-center">Macro Distribution</h4>
                <div className="flex items-center justify-center mb-3">
                  <svg width="200" height="200" viewBox="0 0 200 200" className="transform -rotate-90">
                    {/* Protein Slice */}
                    <circle
                      cx="100"
                      cy="100"
                      r="80"
                      fill="none"
                      stroke="#ef4444"
                      strokeWidth="40"
                      strokeDasharray={`${(results.macro_targets.protein_percentage / 100) * 502.65} 502.65`}
                      strokeDashoffset="0"
                    />
                    {/* Fat Slice */}
                    <circle
                      cx="100"
                      cy="100"
                      r="80"
                      fill="none"
                      stroke="#eab308"
                      strokeWidth="40"
                      strokeDasharray={`${(results.macro_targets.fat_percentage / 100) * 502.65} 502.65`}
                      strokeDashoffset={`-${(results.macro_targets.protein_percentage / 100) * 502.65}`}
                    />
                    {/* Carbs Slice */}
                    <circle
                      cx="100"
                      cy="100"
                      r="80"
                      fill="none"
                      stroke="#22c55e"
                      strokeWidth="40"
                      strokeDasharray={`${(results.macro_targets.carbs_percentage / 100) * 502.65} 502.65`}
                      strokeDashoffset={`-${((results.macro_targets.protein_percentage + results.macro_targets.fat_percentage) / 100) * 502.65}`}
                    />
                  </svg>
                </div>

                {/* Legend */}
                <div className="flex justify-center gap-4 text-xs">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span className="text-gray-700">Protein {results.macro_targets.protein_percentage}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="text-gray-700">Fat {results.macro_targets.fat_percentage}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-gray-700">Carbs {results.macro_targets.carbs_percentage}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Save & Continue Button */}
            <div className="pt-6 border-t-2 border-gray-200">
              <div className="flex gap-3">
                <button
                  onClick={() => { setResults(null); setSaved(false); }}
                  className="flex-1 bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
                >
                  ↻ Recalculate
                </button>
                <button
                  onClick={handleSaveAndContinue}
                  disabled={saving || saved}
                  className="flex-1 bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-green-600 hover:to-blue-700 transition-colors disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <>
                      <div className="flex items-center justify-center gap-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                        Saving...
                      </div>
                    </>
                  ) : saved ? (
                    '✓ Saved! Redirecting...'
                  ) : (
                    'Save & Continue to Workout Planner →'
                  )}
                </button>
              </div>

              {/* Info Message */}
              <p className="text-xs text-gray-500 mt-3 text-center">
                Your targets will be saved and used in the tracking dashboard
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
