'use client';

import { usePathname, useRouter } from 'next/navigation';
import { MessageCircle, HelpCircle, FileQuestion, BookOpen, LogOut, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const navigationItems = [
  {
    name: 'Chat',
    href: '/chat',
    icon: MessageCircle,
  },
  {
    name: 'Q&A',
    href: '/qa',
    icon: HelpCircle,
  },
  {
    name: 'Answer Quiz',
    href: '/answer-questions',
    icon: FileQuestion,
  },
  {
    name: 'Notes',
    href: '/notes',
    icon: BookOpen,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className="fixed left-0 top-20 bottom-0 w-64 bg-sidebar-bg border-r border-border z-40 hidden lg:block">
      <div className="flex flex-col h-full">
        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <a
                key={item.name}
                href={item.href}
                className={`
                  flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200
                  ${isActive
                    ? 'bg-primary text-white shadow-lg'
                    : 'text-text-secondary hover:text-text hover:bg-card-bg'
                  }
                `}
              >
                <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-white' : 'text-text-secondary'}`} />
                {item.name}
              </a>
            );
          })}
        </nav>

        {/* User Profile Section */}
        <div className="border-t border-border p-4">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-primary/10 p-2 rounded-full">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text truncate">
                {user?.username || 'User'}
              </p>
              <p className="text-xs text-text-secondary truncate">
                {user?.email || 'user@example.com'}
              </p>
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-4 py-2 text-sm font-medium text-text-secondary hover:text-text hover:bg-card-bg rounded-lg transition-all duration-200"
          >
            <LogOut className="mr-3 h-4 w-4" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
