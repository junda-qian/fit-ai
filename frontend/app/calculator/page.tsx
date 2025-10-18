import EnergyCalculator from '@/components/energy-calculator';
import Navigation from '@/components/navigation';

export default function CalculatorPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Energy Intake Calculator
            </h1>
            <p className="text-gray-600">
              Calculate your personalized energy expenditure and target intake based on your training schedule
            </p>
          </div>

          <EnergyCalculator />

          <footer className="mt-8 text-center text-sm text-gray-500">
            <p>Based on Cunningham et al. (1991) BMR formula</p>
            <p className="mt-1">For educational purposes. Consult certified nutritionists for personalized guidance</p>
          </footer>
        </div>
      </div>
    </main>
  );
}
