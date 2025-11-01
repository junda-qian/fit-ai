'use client';

import { useState, useEffect } from 'react';
import { Scale, ArrowLeft, TrendingDown, TrendingUp, Calendar, Ruler, Info } from 'lucide-react';
import Navigation from '@/components/navigation';
import Link from 'next/link';

interface BodyLog {
  id: string;
  date: string;
  weight: number;
  body_fat_pct: number | null;
  body_fat_method: string | null;
  skinfolds: Record<string, number> | null;
  skinfold_sum: number | null;
  waist_cm: number | null;
  hips_cm: number | null;
  neck_cm: number | null;
  notes: string | null;
}

type TrackingMode = 'simple' | 'skinfolds' | 'circumferences' | 'bodyfat';

// Skinfold measurement sites with descriptions
const SKINFOLD_SITES = [
  { key: 'tricep', label: 'Tricep', description: 'Back of arm, midway between shoulder and elbow' },
  { key: 'abdomen', label: 'Abdomen', description: '2cm to the right of navel' },
  { key: 'thigh', label: 'Thigh', description: 'Front of thigh, midway between hip and knee' },
  { key: 'suprailiac', label: 'Suprailiac', description: 'Above hip bone, diagonal fold' },
  { key: 'subscapular', label: 'Subscapular', description: 'Below shoulder blade, diagonal fold' },
  { key: 'chest', label: 'Chest', description: 'Between armpit and nipple (males)' },
  { key: 'midaxillary', label: 'Midaxillary', description: 'Side of torso, level with nipple' },
];

const BODY_FAT_METHODS = [
  { value: 'jackson_pollock_3', label: 'Jackson-Pollock 3-Site' },
  { value: 'jackson_pollock_7', label: 'Jackson-Pollock 7-Site' },
  { value: 'navy', label: 'Navy Method (Circumference)' },
  { value: 'bia_scale', label: 'BIA Scale' },
  { value: 'dexa', label: 'DEXA Scan' },
  { value: 'visual', label: 'Visual Estimate' },
];

export default function WeightLogging() {
  // Basic fields
  const [weight, setWeight] = useState('');
  const [notes, setNotes] = useState('');
  const [trackingMode, setTrackingMode] = useState<TrackingMode>('simple');

  // Skinfold measurements
  const [skinfolds, setSkinfolds] = useState<Record<string, string>>({});

  // Circumference measurements
  const [waist, setWaist] = useState('');
  const [hips, setHips] = useState('');
  const [neck, setNeck] = useState('');

  // Body fat tracking
  const [bodyFat, setBodyFat] = useState('');
  const [bodyFatMethod, setBodyFatMethod] = useState('');

  // UI state
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
      startDate.setDate(startDate.getDate() - 30);

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

  const handleSkinfoldChange = (site: string, value: string) => {
    setSkinfolds(prev => ({
      ...prev,
      [site]: value
    }));
  };

  const calculateSkinfoldSum = () => {
    const values = Object.values(skinfolds).filter(v => v !== '').map(parseFloat);
    return values.length > 0 ? values.reduce((sum, val) => sum + val, 0) : null;
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

      // Build skinfolds object (only if values exist)
      const skinfoldData: Record<string, number> = {};
      Object.entries(skinfolds).forEach(([key, value]) => {
        if (value && !isNaN(parseFloat(value))) {
          skinfoldData[key] = parseFloat(value);
        }
      });

      const logData = {
        user_id: userId,
        date: new Date().toISOString().split('T')[0],
        weight: parseFloat(weight),

        // Skinfolds (auto-calculates sum on backend)
        skinfolds: Object.keys(skinfoldData).length > 0 ? skinfoldData : null,

        // Circumferences
        waist_cm: waist ? parseFloat(waist) : null,
        hips_cm: hips ? parseFloat(hips) : null,
        neck_cm: neck ? parseFloat(neck) : null,

        // Body fat
        body_fat_pct: bodyFat ? parseFloat(bodyFat) : null,
        body_fat_method: bodyFatMethod || null,

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
      setSkinfolds({});
      setWaist('');
      setHips('');
      setNeck('');
      setBodyFat('');
      setBodyFatMethod('');
      setNotes('');

      // Refresh logs
      await fetchRecentLogs();

      alert('Body measurements logged successfully!');
    } catch (error) {
      console.error('Error logging weight:', error);
      alert('Failed to log measurements. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const skinfoldSum = calculateSkinfoldSum();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Navigation />

      <div className="max-w-6xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <Link href="/tracking/dashboard" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Scale className="w-8 h-8 text-purple-600" />
            Log Body Measurements
          </h1>
          <p className="text-gray-600">Track weight and body composition with multiple methods</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-6">Today&apos;s Measurement</h2>

              {/* Weight (always shown) */}
              <div className="mb-6">
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
                <p className="text-xs text-gray-500 mt-2">
                  💡 <strong>Recommended:</strong> Measure daily at the same time (e.g., morning, after bathroom, before eating)
                </p>
              </div>

              {/* Tracking Mode Tabs */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Body Composition Tracking (Optional)
                </label>
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <button
                    type="button"
                    onClick={() => setTrackingMode('simple')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      trackingMode === 'simple'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Weight Only
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrackingMode('skinfolds')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      trackingMode === 'skinfolds'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    ⭐ Skinfolds
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrackingMode('circumferences')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      trackingMode === 'circumferences'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <Ruler className="w-4 h-4 inline mr-1" />
                    Circumferences
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrackingMode('bodyfat')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      trackingMode === 'bodyfat'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Body Fat %
                  </button>
                </div>

                {/* Info banner for skinfolds */}
                {trackingMode === 'skinfolds' && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                    <div className="flex items-start gap-2 mb-2">
                      <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm text-blue-800">
                        <strong>⭐ Recommended method!</strong> Skinfolds are most reliable for detecting fat loss trends (not affected by hydration).
                      </div>
                    </div>
                    <div className="text-sm text-blue-700 ml-7">
                      <strong>Measurement frequency:</strong> Weekly (e.g., every Monday morning, same time, fasted)
                    </div>
                    <div className="text-xs text-blue-600 ml-7 mt-1">
                      Daily measurements are unnecessary - fat changes slowly and measuring takes 5-10 minutes
                    </div>
                  </div>
                )}
              </div>

              {/* Skinfold Measurements */}
              {trackingMode === 'skinfolds' && (
                <div className="space-y-3 mb-6">
                  {SKINFOLD_SITES.map(site => (
                    <div key={site.key}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {site.label} (mm)
                      </label>
                      <input
                        type="number"
                        value={skinfolds[site.key] || ''}
                        onChange={(e) => handleSkinfoldChange(site.key, e.target.value)}
                        placeholder="e.g., 12.0"
                        step="0.1"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                      <p className="text-xs text-gray-500 mt-1">{site.description}</p>
                    </div>
                  ))}

                  {skinfoldSum !== null && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 mt-4">
                      <div className="text-sm font-medium text-green-800">
                        Total Sum: <span className="text-lg font-bold">{skinfoldSum.toFixed(1)} mm</span>
                      </div>
                      <p className="text-xs text-green-700 mt-1">
                        Track this number over time to see fat loss progress
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Circumference Measurements */}
              {trackingMode === 'circumferences' && (
                <div className="space-y-4 mb-6">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                    <div className="flex items-start gap-2">
                      <Info className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <div className="text-sm text-green-800">
                          <strong>Simple alternative!</strong> Quick to measure with a tape measure.
                        </div>
                        <div className="text-sm text-green-700 mt-1">
                          <strong>Measurement frequency:</strong> Weekly or bi-weekly (same day/time, morning, fasted)
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Waist (cm) - At navel level
                    </label>
                    <input
                      type="number"
                      value={waist}
                      onChange={(e) => setWaist(e.target.value)}
                      placeholder="e.g., 85.0"
                      step="0.1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hips (cm) - Widest point
                    </label>
                    <input
                      type="number"
                      value={hips}
                      onChange={(e) => setHips(e.target.value)}
                      placeholder="e.g., 98.0"
                      step="0.1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Neck (cm) - For Navy method
                    </label>
                    <input
                      type="number"
                      value={neck}
                      onChange={(e) => setNeck(e.target.value)}
                      placeholder="e.g., 38.0"
                      step="0.1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>
              )}

              {/* Body Fat Percentage */}
              {trackingMode === 'bodyfat' && (
                <div className="space-y-4 mb-6">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                    <div className="flex items-start gap-2 mb-2">
                      <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm text-yellow-800">
                        <strong>⚠️ Less reliable:</strong> Body fat % estimates can vary ±3-5%. Use skinfolds for more reliable trend tracking.
                      </div>
                    </div>
                    <div className="text-sm text-yellow-700 ml-7">
                      <strong>Measurement frequency:</strong> Weekly (if using BIA scale, measure same time/hydration state)
                    </div>
                    <div className="text-xs text-yellow-600 ml-7 mt-1">
                      Daily BIA measurements vary with hydration - weekly trends are more meaningful
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Body Fat %
                    </label>
                    <input
                      type="number"
                      value={bodyFat}
                      onChange={(e) => setBodyFat(e.target.value)}
                      placeholder="e.g., 15.5"
                      step="0.1"
                      min="0"
                      max="100"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Measurement Method
                    </label>
                    <select
                      value={bodyFatMethod}
                      onChange={(e) => setBodyFatMethod(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="">Select method...</option>
                      {BODY_FAT_METHODS.map(method => (
                        <option key={method.value} value={method.value}>
                          {method.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Notes */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (Optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g., Morning measurement, fasted"
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
                {saving ? 'Logging...' : 'Log Measurements'}
              </button>
            </div>
          </div>

          {/* Right Column - History */}
          <div>
            {/* Latest Stats */}
            {!loading && recentLogs.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Latest Measurement</h2>

                <div className="text-center mb-4">
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
                </div>

                {/* Latest skinfold sum */}
                {recentLogs[0].skinfold_sum && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mb-3">
                    <div className="text-sm text-purple-700 font-medium">
                      Skinfold Sum: <span className="text-lg font-bold">{recentLogs[0].skinfold_sum} mm</span>
                    </div>
                  </div>
                )}

                {/* Latest body fat */}
                {recentLogs[0].body_fat_pct && (
                  <div className="text-sm text-gray-700 mb-2">
                    Body Fat: {recentLogs[0].body_fat_pct}%
                    {recentLogs[0].body_fat_method && (
                      <span className="text-gray-500 ml-1">({recentLogs[0].body_fat_method.replace(/_/g, ' ')})</span>
                    )}
                  </div>
                )}

                {/* Latest waist */}
                {recentLogs[0].waist_cm && (
                  <div className="text-sm text-gray-700">
                    Waist: {recentLogs[0].waist_cm} cm
                  </div>
                )}
              </div>
            )}

            {/* Recent History */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-600" />
                Recent History (30 days)
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
                  <p className="text-sm">Log your first measurement above</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {recentLogs.map((log, idx) => {
                    const prevLog = recentLogs[idx + 1];
                    const weightChange = prevLog ? log.weight - prevLog.weight : null;
                    const skinfoldChange = (log.skinfold_sum && prevLog?.skinfold_sum)
                      ? log.skinfold_sum - prevLog.skinfold_sum
                      : null;

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
                          {weightChange !== null && (
                            <div className={`text-sm font-medium ${
                              weightChange > 0 ? 'text-blue-600' : weightChange < 0 ? 'text-green-600' : 'text-gray-600'
                            }`}>
                              {weightChange > 0 ? '+' : ''}{weightChange.toFixed(1)} kg
                            </div>
                          )}
                        </div>

                        {/* Skinfold sum */}
                        {log.skinfold_sum && (
                          <div className="text-sm text-purple-700 mb-1 flex items-center justify-between">
                            <span>Skinfolds: {log.skinfold_sum} mm</span>
                            {skinfoldChange !== null && (
                              <span className={`font-medium ${
                                skinfoldChange < 0 ? 'text-green-600' : skinfoldChange > 0 ? 'text-red-600' : 'text-gray-600'
                              }`}>
                                {skinfoldChange > 0 ? '+' : ''}{skinfoldChange.toFixed(1)} mm
                              </span>
                            )}
                          </div>
                        )}

                        {/* Body fat % */}
                        {log.body_fat_pct && (
                          <div className="text-sm text-gray-600 mb-1">
                            Body Fat: {log.body_fat_pct}%
                            {log.body_fat_method && (
                              <span className="text-gray-400 text-xs ml-1">
                                ({log.body_fat_method.replace(/_/g, ' ')})
                              </span>
                            )}
                          </div>
                        )}

                        {/* Waist */}
                        {log.waist_cm && (
                          <div className="text-sm text-gray-600">
                            Waist: {log.waist_cm} cm
                          </div>
                        )}

                        {/* Notes */}
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
