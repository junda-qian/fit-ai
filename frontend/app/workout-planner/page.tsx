import WorkoutPlanner from '@/components/workout-planner';
import Navigation from '@/components/navigation';

export default function WorkoutPlannerPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              AI Workout Planner
            </h1>
            <p className="text-gray-600">
              Generate your personalized training program based on evidence-based principles
            </p>
          </div>

          <WorkoutPlanner />

          <footer className="mt-8 text-center text-sm text-gray-500">
            <p>Powered by AWS Bedrock AI & Exercise Science</p>
            <p className="mt-1">For educational purposes. Consult certified trainers for personalized guidance</p>
          </footer>
        </div>
      </div>
    </main>
  );
}
