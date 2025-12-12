'use client';

import { useEffect, useState } from 'react';
import { CheckCircle2, ArrowRight, User, Dumbbell, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function DemoPage() {
  const [setupComplete, setSetupComplete] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Automatically set up demo user
    const demoUserId = 'demo_user_90day';
    localStorage.setItem('fit_tracker_user_id', demoUserId);

    // Mark setup as complete after a short delay for visual effect
    setTimeout(() => {
      setSetupComplete(true);
    }, 800);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12">
          {!setupComplete ? (
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Setting up demo account...</h2>
              <p className="text-gray-600">Preparing 90 days of sample fitness data</p>
            </div>
          ) : (
            <div className="text-center">
              <div className="bg-green-50 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="w-12 h-12 text-green-600" />
              </div>

              <h1 className="text-3xl font-bold text-gray-900 mb-4">Demo Account Ready!</h1>

              <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 mb-8">
                <div className="flex items-center gap-3 mb-3">
                  <User className="w-5 h-5 text-blue-600" />
                  <h3 className="font-bold text-gray-800">Demo User: demo_user_90day</h3>
                </div>
                <p className="text-gray-700 text-sm text-left">
                  You now have access to 90 days of pre-populated fitness data including:
                </p>
                <ul className="text-sm text-gray-700 text-left mt-3 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Workout Logs:</strong> Complete training history with exercises, sets, reps, and RPE</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Nutrition Logs:</strong> Daily meal tracking with macros and calories</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Body Metrics:</strong> Weight tracking and body composition data</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Progress Trends:</strong> Visualizations showing your fitness journey</span>
                  </li>
                </ul>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <Link
                  href="/tracking/progress"
                  className="flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-4 rounded-xl font-semibold hover:shadow-lg transition-all transform hover:scale-105"
                >
                  <TrendingUp className="w-5 h-5" />
                  View Progress
                  <ArrowRight className="w-5 h-5" />
                </Link>

                <Link
                  href="/tracking/dashboard"
                  className="flex items-center justify-center gap-2 bg-white border-2 border-blue-600 text-blue-600 px-6 py-4 rounded-xl font-semibold hover:bg-blue-50 transition-all"
                >
                  <Dumbbell className="w-5 h-5" />
                  Tracking Dashboard
                </Link>
              </div>

              <p className="text-sm text-gray-500">
                This demo account has all tracking features enabled. Explore the dashboards to see your AI fitness assistant in action!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
