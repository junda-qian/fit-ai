'use client';

import { useEffect, useState } from 'react';
import { Brain, Calculator, Dumbbell, TrendingUp, ArrowRight, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

interface UserProgress {
  hasProfile: boolean;
  hasWorkoutPlan: boolean;
  userId: string | null;
}

export default function HomePage() {
  const [progress, setProgress] = useState<UserProgress>({
    hasProfile: false,
    hasWorkoutPlan: false,
    userId: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUserProgress();
  }, []);

  const checkUserProgress = async () => {
    try {
      const userId = localStorage.getItem('fit_tracker_user_id');
      if (!userId) {
        setLoading(false);
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // Check if user has profile
      const profileRes = await fetch(`${apiUrl}/api/user-profile/${userId}`);
      const hasProfile = profileRes.ok;

      // Check if user has workout plan
      const planRes = await fetch(`${apiUrl}/api/workout-plan/${userId}/active`);
      const hasWorkoutPlan = planRes.ok;

      setProgress({
        hasProfile,
        hasWorkoutPlan,
        userId
      });
    } catch (error) {
      console.error('Error checking user progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: Brain,
      title: 'AI Fitness Chatbot',
      description: 'Get evidence-based answers to your fitness questions powered by scientific research and RAG technology.',
      href: '/chatbot',
      color: 'from-purple-500 to-purple-700',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      available: true
    },
    {
      icon: Calculator,
      title: 'Energy Calculator',
      description: 'Calculate your personalized calorie and macro targets based on your goals, activity level, and body composition.',
      href: '/calculator',
      color: 'from-blue-500 to-blue-700',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      available: true,
      completed: progress.hasProfile
    },
    {
      icon: Dumbbell,
      title: 'Workout Planner',
      description: 'Generate personalized workout programs tailored to your experience level, schedule, and training goals.',
      href: '/workout-planner',
      color: 'from-green-500 to-green-700',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      available: true,
      completed: progress.hasWorkoutPlan
    },
    {
      icon: TrendingUp,
      title: 'Tracking Dashboard',
      description: 'Track your nutrition, workouts, and progress all in one place. Monitor your daily macros and workout completion.',
      href: '/tracking/dashboard',
      color: 'from-orange-500 to-orange-700',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      available: progress.hasProfile,
      requiresSetup: !progress.hasProfile
    }
  ];

  // Determine next recommended step
  const getRecommendedAction = () => {
    if (!progress.hasProfile) {
      return {
        title: 'Get Started',
        description: 'Begin by calculating your energy targets',
        href: '/calculator',
        cta: 'Calculate My Targets'
      };
    }
    if (!progress.hasWorkoutPlan) {
      return {
        title: 'Next Step',
        description: 'Create your personalized workout plan',
        href: '/workout-planner',
        cta: 'Generate Workout Plan'
      };
    }
    return {
      title: 'Continue Tracking',
      description: 'View your dashboard and log your progress',
      href: '/tracking/dashboard',
      cta: 'Go to Dashboard'
    };
  };

  const recommendedAction = getRecommendedAction();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Evidence-Based
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Fitness Tracking</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Your all-in-one platform for science-backed fitness guidance, personalized nutrition planning,
            workout programming, and comprehensive progress tracking.
          </p>

          {/* Progress Indicator */}
          {progress.userId && (
            <div className="inline-flex items-center gap-4 bg-white rounded-full px-6 py-3 shadow-md mb-8">
              <div className="flex items-center gap-2">
                {progress.hasProfile ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                ) : (
                  <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                )}
                <span className="text-sm font-medium text-gray-700">Profile</span>
              </div>
              <div className="flex items-center gap-2">
                {progress.hasWorkoutPlan ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                ) : (
                  <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                )}
                <span className="text-sm font-medium text-gray-700">Workout Plan</span>
              </div>
            </div>
          )}

          {/* Recommended Action CTA */}
          <Link
            href={recommendedAction.href}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all transform hover:scale-105"
          >
            {recommendedAction.cta}
            <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="text-sm text-gray-500 mt-3">{recommendedAction.description}</p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            const isDisabled = !feature.available;

            return (
              <Link
                key={index}
                href={isDisabled ? '#' : feature.href}
                className={`group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all transform hover:scale-105 overflow-hidden ${
                  isDisabled ? 'opacity-60 cursor-not-allowed' : ''
                }`}
                onClick={(e) => {
                  if (isDisabled) e.preventDefault();
                }}
              >
                {/* Gradient Header */}
                <div className={`h-2 bg-gradient-to-r ${feature.color}`} />

                <div className="p-8">
                  {/* Icon & Status */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`${feature.bgColor} p-4 rounded-xl`}>
                      <Icon className={`w-8 h-8 ${feature.iconColor}`} />
                    </div>
                    {feature.completed && (
                      <div className="flex items-center gap-1 bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                        <CheckCircle2 className="w-4 h-4" />
                        Complete
                      </div>
                    )}
                    {feature.requiresSetup && (
                      <div className="bg-yellow-50 text-yellow-700 px-3 py-1 rounded-full text-sm font-medium">
                        Setup Required
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-600 mb-6">{feature.description}</p>

                  {/* CTA */}
                  <div className="flex items-center gap-2 text-blue-600 font-semibold group-hover:gap-3 transition-all">
                    {isDisabled ? (
                      <>Complete setup first</>
                    ) : feature.completed ? (
                      <>View {feature.title.split(' ')[0]}</>
                    ) : (
                      <>Get Started</>
                    )}
                    <ArrowRight className="w-5 h-5" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Quick Info Section */}
        <div className="mt-16 text-center">
          <div className="inline-block bg-white rounded-2xl shadow-lg px-8 py-6 max-w-2xl">
            <h3 className="text-xl font-bold text-gray-900 mb-3">How It Works</h3>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center font-bold">1</div>
                <span>Calculate targets</span>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 hidden md:block" />
              <div className="flex items-center gap-2">
                <div className="bg-green-100 text-green-600 rounded-full w-6 h-6 flex items-center justify-center font-bold">2</div>
                <span>Generate plan</span>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 hidden md:block" />
              <div className="flex items-center gap-2">
                <div className="bg-orange-100 text-orange-600 rounded-full w-6 h-6 flex items-center justify-center font-bold">3</div>
                <span>Track progress</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
