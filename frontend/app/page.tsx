import HealthChat from '@/components/health-chat';
import Navigation from '@/components/navigation';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Evidence-Based Fitness Coach
            </h1>
            <p className="text-gray-600">
              Your AI-powered fitness companion for optimal health, training, nutrition, and performance
            </p>
          </div>

          <Navigation />

          <div className="h-[650px]">
            <HealthChat />
          </div>

          <footer className="mt-8 text-center text-sm text-gray-500">
            <p>Powered by AWS Bedrock & RAG Architecture</p>
            <p className="mt-1">For educational purposes. Consult certified fitness professionals for personalized guidance</p>
          </footer>
        </div>
      </div>
    </main>
  );
}