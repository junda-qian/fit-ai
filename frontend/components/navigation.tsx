'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageSquare, Calculator, Dumbbell } from 'lucide-react';

export default function Navigation() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Fitness Chatbot', icon: MessageSquare },
    { href: '/calculator', label: 'Energy Calculator', icon: Calculator },
    { href: '/workout-planner', label: 'Workout Planner', icon: Dumbbell },
  ];

  return (
    <nav className="mb-8">
      <div className="flex justify-center gap-4">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;

          return (
            <Link
              key={link.href}
              href={link.href}
              className={`
                flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all
                ${isActive
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/50 text-gray-600 hover:bg-white hover:shadow-md'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
