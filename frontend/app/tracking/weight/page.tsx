'use client';

import { useState, useEffect } from 'react';
import { Scale, ArrowLeft, TrendingDown, TrendingUp, Calendar } from 'lucide-react';
import Navigation from '@/components/navigation';
import Link from 'next/link';

interface BodyLog {
  id: string;
  date: string;
  weight: number;
  body_fat_pct: number | null;
  notes: string | null;
}

export default function WeightLogging() {
  const [weight, setWeight] = useState('');
  const [bodyFat, setBodyFat] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [recentLogs, setRecentLogs] = useState<BodyLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentLogs();
  }, []);

  const fetchRecentLogs = async () => {
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) {
        setLoading(false);
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30); // Last 30 days

      const response = await fetch(
        `${apiUrl}/api/body/logs?user_id=${userId}&start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}`
      );

      if (response.ok) {
        const data = await response.json();
        setRecentLogs(data || []);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogWeight = async () => {
    if (!weight) {
      alert('Please enter your weight');
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
        weight: parseFloat(weight),
        body_fat_pct: bodyFat ? parseFloat(bodyFat) : null,
        notes: notes || null
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/body/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
      });

      if (!response.ok) throw new Error('Failed to log weight');

      // Reset form
      setWeight('');
      setBodyFat('');
      setNotes('');

      // Refresh logs
      await fetchRecentLogs();

      alert('Weight logged successfully!');
    } catch (error) {
      console.error('Error logging weight:', error);
      alert('Failed to log weight. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const calculateWeightChange = () => {
    if (recentLogs.length < 2) return null;
    const latest = recentLogs[0].weight;
    const earliest = recentLogs[recentLogs.length - 1].weight;
    const change = latest - earliest;
    return {
      value: Math.abs(change),
      trend: change > 0 ? 'up' : change < 0 ? 'down' : 'stable'
    };
  };

  const weightChange = calculateWeightChange();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Navigation />

      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <Link href="/tracking/dashboard" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Scale className="w-8 h-8 text-purple-600" />
            Log Body Weight
          </h1>
          <p className="text-gray-600">Track your weight and body composition</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-6">Today&apos;s Measurement</h2>

              <div className="space-y-6">
                {/* Weight Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Body Weight (kg) *
                  </label>
                  <input
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    placeholder="e.g., 75.5"
                    step="0.1"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                {/* Body Fat Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Body Fat % (Optional)
                  </label>
                  <input
                    type="number"
                    value={bodyFat}
                    onChange={(e) => setBodyFat(e.target.value)}
                    placeholder="e.g., 15.5"
                    step="0.1"
                    min="0"
                    max="100"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    From scale measurement, caliper, or DEXA scan
                  </p>
                </div>

                {/* Notes Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="e.g., Morning measurement before breakfast"
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                {/* Submit Button */}
                <button
                  onClick={handleLogWeight}
                  disabled={saving || !weight}
                  className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
                >
                  <Scale className="w-5 h-5" />
                  {saving ? 'Logging...' : 'Log Weight'}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Progress & History */}
          <div>
            {/* Weight Change Summary */}
            {!loading && recentLogs.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Latest Measurement</h2>

                <div className="text-center mb-6">
                  <div className="text-5xl font-bold text-gray-800 mb-2">
                    {recentLogs[0].weight}
                    <span className="text-2xl text-gray-600 ml-2">kg</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {new Date(recentLogs[0].date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </div>
                  {recentLogs[0].body_fat_pct && (
                    <div className="mt-2 text-gray-700">
                      Body Fat: {recentLogs[0].body_fat_pct}%
                    </div>
                  )}
                </div>

                {weightChange && weightChange.trend !== 'stable' && (
                  <div className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg ${
                    weightChange.trend === 'up' ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'
                  }`}>
                    {weightChange.trend === 'up' ? (
                      <TrendingUp className="w-5 h-5" />
                    ) : (
                      <TrendingDown className="w-5 h-5" />
                    )}
                    <span className="font-semibold">
                      {weightChange.trend === 'up' ? '+' : '-'}{weightChange.value.toFixed(1)} kg
                    </span>
                    <span className="text-sm">over last 30 days</span>
                  </div>
                )}
              </div>
            )}

            {/* Recent History */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-600" />
                Recent History
              </h2>

              {loading ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-2" />
                  Loading...
                </div>
              ) : recentLogs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Scale className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>No measurements yet</p>
                  <p className="text-sm">Log your first weight above</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {recentLogs.map((log, idx) => {
                    const prevLog = recentLogs[idx + 1];
                    const change = prevLog ? log.weight - prevLog.weight : null;

                    return (
                      <div key={log.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-bold text-gray-800 text-xl">
                              {log.weight} kg
                            </div>
                            <div className="text-sm text-gray-600">
                              {new Date(log.date).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                              })}
                            </div>
                          </div>
                          {change !== null && (
                            <div className={`text-sm font-medium ${
                              change > 0 ? 'text-blue-600' : change < 0 ? 'text-green-600' : 'text-gray-600'
                            }`}>
                              {change > 0 ? '+' : ''}{change.toFixed(1)} kg
                            </div>
                          )}
                        </div>
                        {log.body_fat_pct && (
                          <div className="text-sm text-gray-600 mb-2">
                            Body Fat: {log.body_fat_pct}%
                          </div>
                        )}
                        {log.notes && (
                          <div className="text-sm text-gray-600 italic mt-2 pt-2 border-t border-gray-100">
                            &quot;{log.notes}&quot;
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
