'use client';

import { useState, useEffect } from 'react';
import { Search, Plus, Trash2, Utensils, Clock, ArrowLeft } from 'lucide-react';
import Navigation from '@/components/navigation';
import Link from 'next/link';

interface USDAFood {
  fdc_id: number;
  description: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  serving_size: string;
  serving_unit: string;
}

interface FoodItem {
  name: string;
  amount: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  fdc_id?: number;
}

interface NutritionLog {
  id: string;
  meal_type: string;
  time: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  food_items: FoodItem[];
}

export default function NutritionLogging() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<USDAFood[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedFoods, setSelectedFoods] = useState<FoodItem[]>([]);
  const [mealType, setMealType] = useState('breakfast');
  const [todaysLogs, setTodaysLogs] = useState<NutritionLog[]>([]);
  const [saving, setSaving] = useState(false);
  const [portionInputs, setPortionInputs] = useState<Record<number, string>>({});

  useEffect(() => {
    fetchTodaysLogs();
  }, []);

  const fetchTodaysLogs = async () => {
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) return;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const today = new Date().toISOString().split('T')[0];
      const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

      const response = await fetch(
        `${apiUrl}/api/nutrition/logs?user_id=${userId}&start_date=${today}&end_date=${tomorrow}`
      );

      if (response.ok) {
        const data = await response.json();
        setTodaysLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery || searchQuery.length < 2) return;

    setSearching(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${apiUrl}/api/food/search?query=${encodeURIComponent(searchQuery)}&page_size=15`
      );

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.foods || []);
      }
    } catch (error) {
      console.error('Error searching foods:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleAddFood = (food: USDAFood) => {
    // Get custom portion or use default serving size
    const customGrams = portionInputs[food.fdc_id];
    const grams = customGrams ? parseFloat(customGrams) : parseFloat(food.serving_size);

    // Calculate multiplier based on serving size (usually 100g)
    const multiplier = grams / parseFloat(food.serving_size);

    const foodItem: FoodItem = {
      name: food.description,
      amount: `${grams}${food.serving_unit}`,
      calories: food.calories * multiplier,
      protein: food.protein * multiplier,
      carbs: food.carbs * multiplier,
      fats: food.fats * multiplier,
      fdc_id: food.fdc_id
    };

    setSelectedFoods([...selectedFoods, foodItem]);
    setSearchQuery('');
    setSearchResults([]);
    // Clear the portion input for this food
    setPortionInputs(prev => {
      const newInputs = { ...prev };
      delete newInputs[food.fdc_id];
      return newInputs;
    });
  };

  const handleRemoveFood = (index: number) => {
    setSelectedFoods(selectedFoods.filter((_, i) => i !== index));
  };

  const calculateTotals = () => {
    return selectedFoods.reduce(
      (totals, food) => ({
        calories: totals.calories + food.calories,
        protein: totals.protein + food.protein,
        carbs: totals.carbs + food.carbs,
        fats: totals.fats + food.fats
      }),
      { calories: 0, protein: 0, carbs: 0, fats: 0 }
    );
  };

  const handleLogMeal = async () => {
    if (selectedFoods.length === 0) {
      alert('Please add at least one food item');
      return;
    }

    setSaving(true);
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) {
        alert('Please complete the Energy Calculator first');
        window.location.href = '/calculator';
        return;
      }

      const totals = calculateTotals();
      const now = new Date();

      const logData = {
        user_id: userId,
        date: now.toISOString().split('T')[0],
        meal_type: mealType,
        time: now.toTimeString().split(' ')[0],
        calories: totals.calories,
        protein: totals.protein,
        carbs: totals.carbs,
        fats: totals.fats,
        food_items: selectedFoods.map(f => ({
          name: f.name,
          amount: f.amount,
          calories: f.calories,
          protein: f.protein,
          carbs: f.carbs,
          fats: f.fats,
          fdc_id: f.fdc_id
        })),
        notes: null
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/nutrition/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
      });

      if (!response.ok) throw new Error('Failed to log meal');

      // Reset form
      setSelectedFoods([]);
      setSearchResults([]);

      // Refresh today's logs
      await fetchTodaysLogs();

      alert('Meal logged successfully!');
    } catch (error) {
      console.error('Error logging meal:', error);
      alert('Failed to log meal. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const totals = calculateTotals();

  const mealTypes = [
    { value: 'breakfast', label: 'Breakfast', emoji: '🌅' },
    { value: 'lunch', label: 'Lunch', emoji: '☀️' },
    { value: 'dinner', label: 'Dinner', emoji: '🌙' },
    { value: 'snack', label: 'Snack', emoji: '🍎' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-yellow-50">
      <Navigation />

      <div className="max-w-6xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <Link href="/tracking/dashboard" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Utensils className="w-8 h-8 text-orange-600" />
            Log Nutrition
          </h1>
          <p className="text-gray-600">Search foods and track your meals</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Food Search & Selection */}
          <div>
            {/* Meal Type Selection */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Meal Type</h2>
              <div className="grid grid-cols-2 gap-3">
                {mealTypes.map(meal => (
                  <button
                    key={meal.value}
                    onClick={() => setMealType(meal.value)}
                    className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all ${
                      mealType === meal.value
                        ? 'bg-orange-600 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <span>{meal.emoji}</span>
                    {meal.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Food Search */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Search Foods</h2>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search for food... (e.g., banana, chicken breast)"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={searching || searchQuery.length < 2}
                  className="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
                >
                  <Search className="w-4 h-4" />
                  {searching ? 'Searching...' : 'Search'}
                </button>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {searchResults.map((food) => {
                    const portionGrams = portionInputs[food.fdc_id] || food.serving_size;
                    const multiplier = parseFloat(portionGrams) / parseFloat(food.serving_size);

                    return (
                      <div
                        key={food.fdc_id}
                        className="border border-gray-200 rounded-lg p-3 hover:border-orange-500 transition-colors"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-semibold text-gray-800 flex-1">{food.description}</h3>
                        </div>

                        {/* Portion Input */}
                        <div className="mb-3 flex items-center gap-2">
                          <label className="text-sm text-gray-600">Amount:</label>
                          <input
                            type="number"
                            value={portionInputs[food.fdc_id] || ''}
                            onChange={(e) => setPortionInputs({
                              ...portionInputs,
                              [food.fdc_id]: e.target.value
                            })}
                            placeholder={food.serving_size}
                            className="w-24 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                            onClick={(e) => e.stopPropagation()}
                          />
                          <span className="text-sm text-gray-600">{food.serving_unit}</span>
                          <button
                            onClick={() => handleAddFood(food)}
                            className="ml-auto bg-orange-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-orange-700 flex items-center gap-1"
                          >
                            <Plus className="w-3 h-3" />
                            Add
                          </button>
                        </div>

                        {/* Nutritional Info */}
                        <div className="text-sm text-gray-600 grid grid-cols-2 gap-2 bg-gray-50 rounded p-2">
                          <div>Per {portionGrams}{food.serving_unit}</div>
                          <div className="text-right font-medium text-orange-600">
                            {Math.round(food.calories * multiplier)} cal
                          </div>
                          <div>Protein: {Math.round(food.protein * multiplier)}g</div>
                          <div className="text-right">Carbs: {Math.round(food.carbs * multiplier)}g</div>
                          <div>Fats: {Math.round(food.fats * multiplier)}g</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {searching && (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto mb-2" />
                  Searching USDA database...
                </div>
              )}

              {!searching && searchResults.length === 0 && searchQuery && (
                <div className="text-center py-8 text-gray-500">
                  No results found. Try a different search term.
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Selected Foods & Totals */}
          <div>
            {/* Selected Foods */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Selected Foods</h2>

              {selectedFoods.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Utensils className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>No foods added yet</p>
                  <p className="text-sm">Search and add foods above</p>
                </div>
              ) : (
                <div className="space-y-3 mb-6">
                  {selectedFoods.map((food, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-800">{food.name}</h3>
                          <p className="text-sm text-gray-600">{food.amount}</p>
                        </div>
                        <button
                          onClick={() => handleRemoveFood(index)}
                          className="text-red-600 hover:text-red-700 p-1"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="grid grid-cols-4 gap-2 text-sm text-gray-600">
                        <div className="text-center">
                          <div className="font-medium text-gray-800">{Math.round(food.calories)}</div>
                          <div className="text-xs">cal</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-800">{Math.round(food.protein)}g</div>
                          <div className="text-xs">protein</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-800">{Math.round(food.carbs)}g</div>
                          <div className="text-xs">carbs</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-800">{Math.round(food.fats)}g</div>
                          <div className="text-xs">fats</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Totals */}
              {selectedFoods.length > 0 && (
                <>
                  <div className="border-t pt-4 mb-4">
                    <h3 className="font-bold text-gray-800 mb-3">Meal Totals</h3>
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div className="bg-orange-50 rounded-lg p-3">
                        <div className="text-2xl font-bold text-orange-600">{Math.round(totals.calories)}</div>
                        <div className="text-xs text-gray-600">Calories</div>
                      </div>
                      <div className="bg-red-50 rounded-lg p-3">
                        <div className="text-2xl font-bold text-red-600">{Math.round(totals.protein)}g</div>
                        <div className="text-xs text-gray-600">Protein</div>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-3">
                        <div className="text-2xl font-bold text-yellow-600">{Math.round(totals.fats)}g</div>
                        <div className="text-xs text-gray-600">Fats</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3">
                        <div className="text-2xl font-bold text-green-600">{Math.round(totals.carbs)}g</div>
                        <div className="text-xs text-gray-600">Carbs</div>
                      </div>
                    </div>
                  </div>

                  {/* Log Button */}
                  <button
                    onClick={handleLogMeal}
                    disabled={saving}
                    className="w-full bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
                  >
                    <Plus className="w-5 h-5" />
                    {saving ? 'Logging...' : 'Log Meal'}
                  </button>
                </>
              )}
            </div>

            {/* Today's Logs */}
            {todaysLogs.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-600" />
                  Today's Meals
                </h2>
                <div className="space-y-4">
                  {/* Group logs by meal type */}
                  {mealTypes.map(mealType => {
                    const mealsOfType = todaysLogs.filter(log => log.meal_type === mealType.value);
                    if (mealsOfType.length === 0) return null;

                    // Calculate totals for this meal type
                    const totalCalories = mealsOfType.reduce((sum, log) => sum + log.calories, 0);
                    const totalProtein = mealsOfType.reduce((sum, log) => sum + log.protein, 0);
                    const totalCarbs = mealsOfType.reduce((sum, log) => sum + log.carbs, 0);
                    const totalFats = mealsOfType.reduce((sum, log) => sum + log.fats, 0);

                    // Collect all food items from all logs of this meal type
                    const allFoodItems = mealsOfType.flatMap(log => log.food_items);

                    return (
                      <div key={mealType.value} className="border border-gray-200 rounded-lg p-4">
                        {/* Meal Type Header */}
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-2xl">{mealType.emoji}</span>
                          <span className="font-bold text-gray-800 text-lg capitalize">{mealType.label}</span>
                          <span className="text-sm text-gray-500 ml-auto">
                            {mealsOfType.length} {mealsOfType.length === 1 ? 'entry' : 'entries'}
                          </span>
                        </div>

                        {/* Food Items */}
                        <div className="space-y-2 mb-3">
                          {allFoodItems.map((item, idx) => (
                            <div key={idx} className="flex justify-between items-center text-sm bg-gray-50 rounded px-3 py-2">
                              <div className="flex-1">
                                <span className="text-gray-800">{item.name}</span>
                                <span className="text-gray-500 text-xs ml-2">({item.amount})</span>
                              </div>
                              <div className="text-xs text-gray-600">
                                {Math.round(item.calories)} cal
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Totals */}
                        <div className="grid grid-cols-4 gap-2 text-sm text-center border-t pt-3">
                          <div>
                            <div className="font-bold text-orange-600">{Math.round(totalCalories)}</div>
                            <div className="text-xs text-gray-600">cal</div>
                          </div>
                          <div>
                            <div className="font-bold text-red-600">{Math.round(totalProtein)}g</div>
                            <div className="text-xs text-gray-600">protein</div>
                          </div>
                          <div>
                            <div className="font-bold text-yellow-600">{Math.round(totalFats)}g</div>
                            <div className="text-xs text-gray-600">fats</div>
                          </div>
                          <div>
                            <div className="font-bold text-green-600">{Math.round(totalCarbs)}g</div>
                            <div className="text-xs text-gray-600">carbs</div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
