'use client';

import { useState, useEffect } from 'react';
import { Dumbbell, Plus, Trash2, ArrowLeft, Clock, Save } from 'lucide-react';
import Navigation from '@/components/navigation';
import Link from 'next/link';

interface ExerciseSet {
  reps: number;
  weight: number;
  rpe: number;
}

interface WorkoutExercise {
  name: string;
  sets: ExerciseSet[];
}

interface WorkoutLog {
  id: string;
  date: string;
  workout_name: string;
  exercises: WorkoutExercise[];
  duration_minutes: number;
  notes: string | null;
  completed: boolean;
}

interface Exercise {
  name: string;
  sets: number;
  reps: string;
  rpe: number;
  muscle_group: string;
  day: string;
}

export default function WorkoutLogging() {
  const [workoutName, setWorkoutName] = useState('');
  const [exercises, setExercises] = useState<WorkoutExercise[]>([]);
  const [currentExercise, setCurrentExercise] = useState('');
  const [currentSets, setCurrentSets] = useState<ExerciseSet[]>([]);
  const [duration, setDuration] = useState(60);
  const [notes, setNotes] = useState('');
  const [todaysWorkouts, setTodaysWorkouts] = useState<WorkoutLog[]>([]);
  const [planExercises, setPlanExercises] = useState<Exercise[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchWorkoutPlan();
    fetchTodaysWorkouts();
  }, []);

  const fetchWorkoutPlan = async () => {
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) return;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/workout-plan/${userId}/active`);

      if (response.ok) {
        const data = await response.json();
        setPlanExercises(data.exercises || []);
        if (data.plan_name) {
          setWorkoutName(data.plan_name);
        }
      }
    } catch (error) {
      console.error('Error fetching workout plan:', error);
    }
  };

  const fetchTodaysWorkouts = async () => {
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) return;

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const today = new Date().toISOString().split('T')[0];
      const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

      const response = await fetch(
        `${apiUrl}/api/workout/logs?user_id=${userId}&start_date=${today}&end_date=${tomorrow}`
      );

      if (response.ok) {
        const data = await response.json();
        setTodaysWorkouts(data.logs || []);
      }
    } catch (error) {
      console.error('Error fetching workouts:', error);
    }
  };

  const handleAddSet = () => {
    setCurrentSets([...currentSets, { reps: 10, weight: 0, rpe: 7 }]);
  };

  const handleUpdateSet = (index: number, field: keyof ExerciseSet, value: number) => {
    const newSets = [...currentSets];
    newSets[index] = { ...newSets[index], [field]: value };
    setCurrentSets(newSets);
  };

  const handleRemoveSet = (index: number) => {
    setCurrentSets(currentSets.filter((_, i) => i !== index));
  };

  const handleAddExercise = () => {
    if (!currentExercise || currentSets.length === 0) {
      alert('Please enter exercise name and add at least one set');
      return;
    }

    setExercises([...exercises, {
      name: currentExercise,
      sets: currentSets
    }]);

    // Reset
    setCurrentExercise('');
    setCurrentSets([]);
  };

  const handleRemoveExercise = (index: number) => {
    setExercises(exercises.filter((_, i) => i !== index));
  };

  const handleSelectPlanExercise = (exercise: Exercise) => {
    setCurrentExercise(exercise.name);
    // Initialize sets based on plan
    const numSets = exercise.sets || 3;
    const defaultReps = parseInt(exercise.reps.split('-')[0]) || 10;
    const initialSets = Array(numSets).fill(null).map(() => ({
      reps: defaultReps,
      weight: 0,
      rpe: exercise.rpe || 7
    }));
    setCurrentSets(initialSets);
  };

  const handleLogWorkout = async () => {
    if (exercises.length === 0) {
      alert('Please add at least one exercise');
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

      const logData = {
        user_id: userId,
        date: new Date().toISOString().split('T')[0],
        workout_name: workoutName || 'Workout',
        exercises: exercises,
        duration_minutes: duration,
        notes: notes || null,
        completed: true
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/workout/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
      });

      if (!response.ok) throw new Error('Failed to log workout');

      // Reset form
      setExercises([]);
      setCurrentExercise('');
      setCurrentSets([]);
      setNotes('');

      // Refresh today's workouts
      await fetchTodaysWorkouts();

      alert('Workout logged successfully!');
    } catch (error) {
      console.error('Error logging workout:', error);
      alert('Failed to log workout. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Navigation />

      <div className="max-w-6xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <Link href="/tracking/dashboard" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Dumbbell className="w-8 h-8 text-blue-600" />
            Log Workout
          </h1>
          <p className="text-gray-600">Track your training session</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Exercise Input */}
          <div>
            {/* Workout Name */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Workout Details</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Workout Name
                  </label>
                  <input
                    type="text"
                    value={workoutName}
                    onChange={(e) => setWorkoutName(e.target.value)}
                    placeholder="e.g., Upper Body Day A"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Quick Select from Plan */}
            {planExercises.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Quick Select from Plan</h2>
                <div className="max-h-64 overflow-y-auto space-y-2">
                  {planExercises.map((exercise, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSelectPlanExercise(exercise)}
                      className="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                    >
                      <div className="font-semibold text-gray-800">{exercise.name}</div>
                      <div className="text-sm text-gray-600">
                        {exercise.sets} sets × {exercise.reps} reps • {exercise.muscle_group}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Add Exercise */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Add Exercise</h2>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Exercise Name
                </label>
                <input
                  type="text"
                  value={currentExercise}
                  onChange={(e) => setCurrentExercise(e.target.value)}
                  placeholder="e.g., Bench Press"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Sets */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-gray-700">Sets</label>
                  <button
                    onClick={handleAddSet}
                    className="text-sm bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 flex items-center gap-1"
                  >
                    <Plus className="w-3 h-3" />
                    Add Set
                  </button>
                </div>

                {currentSets.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 border border-dashed border-gray-300 rounded-lg">
                    No sets added yet. Click "Add Set" to begin.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {currentSets.map((set, idx) => (
                      <div key={idx} className="flex items-center gap-2 bg-gray-50 p-3 rounded-lg">
                        <span className="text-sm font-medium text-gray-600 w-12">Set {idx + 1}</span>
                        <input
                          type="number"
                          value={set.reps}
                          onChange={(e) => handleUpdateSet(idx, 'reps', parseInt(e.target.value))}
                          placeholder="Reps"
                          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="text-xs text-gray-600">reps @</span>
                        <input
                          type="number"
                          value={set.weight}
                          onChange={(e) => handleUpdateSet(idx, 'weight', parseFloat(e.target.value))}
                          placeholder="Weight"
                          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="text-xs text-gray-600">kg</span>
                        <input
                          type="number"
                          value={set.rpe}
                          onChange={(e) => handleUpdateSet(idx, 'rpe', parseFloat(e.target.value))}
                          placeholder="RPE"
                          min="1"
                          max="10"
                          step="0.5"
                          className="w-16 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="text-xs text-gray-600">RPE</span>
                        <button
                          onClick={() => handleRemoveSet(idx)}
                          className="ml-auto text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={handleAddExercise}
                disabled={!currentExercise || currentSets.length === 0}
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Exercise to Workout
              </button>
            </div>
          </div>

          {/* Right Column - Workout Summary */}
          <div>
            {/* Current Workout */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Workout Summary</h2>

              {exercises.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Dumbbell className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>No exercises added yet</p>
                  <p className="text-sm">Add exercises on the left</p>
                </div>
              ) : (
                <>
                  <div className="space-y-4 mb-6">
                    {exercises.map((exercise, idx) => (
                      <div key={idx} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <h3 className="font-bold text-gray-800">{exercise.name}</h3>
                          <button
                            onClick={() => handleRemoveExercise(idx)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="space-y-2">
                          {exercise.sets.map((set, setIdx) => (
                            <div key={setIdx} className="flex justify-between text-sm bg-gray-50 px-3 py-2 rounded">
                              <span className="text-gray-600">Set {setIdx + 1}</span>
                              <span className="font-medium text-gray-800">
                                {set.reps} reps @ {set.weight} kg • RPE {set.rpe}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Notes */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes (Optional)
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="How did the workout feel? Any observations?"
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Log Button */}
                  <button
                    onClick={handleLogWorkout}
                    disabled={saving}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
                  >
                    <Save className="w-5 h-5" />
                    {saving ? 'Logging...' : 'Log Workout'}
                  </button>
                </>
              )}
            </div>

            {/* Today's Workouts */}
            {todaysWorkouts.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  Today's Workouts
                </h2>
                <div className="space-y-4">
                  {todaysWorkouts.map((workout) => (
                    <div key={workout.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="font-bold text-gray-800">{workout.workout_name}</h3>
                        <span className="text-sm text-gray-600">{workout.duration_minutes} min</span>
                      </div>
                      <div className="space-y-2">
                        {workout.exercises.map((exercise, idx) => (
                          <div key={idx} className="bg-gray-50 rounded p-2">
                            <div className="font-semibold text-sm text-gray-800 mb-1">
                              {exercise.name}
                            </div>
                            <div className="text-xs text-gray-600">
                              {exercise.sets.length} sets
                            </div>
                          </div>
                        ))}
                      </div>
                      {workout.notes && (
                        <div className="mt-3 text-sm text-gray-600 italic">
                          "{workout.notes}"
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
