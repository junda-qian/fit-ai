'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, MessageSquare, Calculator, Dumbbell, TrendingUp, BarChart3 } from 'lucide-react';

export default function Navigation() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/chatbot', label: 'AI Chatbot', icon: MessageSquare },
    { href: '/calculator', label: 'Calculator', icon: Calculator },
    { href: '/workout-planner', label: 'Planner', icon: Dumbbell },
    { href: '/tracking/dashboard', label: 'Dashboard', icon: TrendingUp },
    { href: '/tracking/progress', label: 'Progress', icon: BarChart3 },
  ];

  return (
    <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-center gap-2 py-4">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;

            return (
              <Link
                key={link.href}
                href={link.href}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all text-sm
                  ${isActive
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-blue-600'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{link.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
