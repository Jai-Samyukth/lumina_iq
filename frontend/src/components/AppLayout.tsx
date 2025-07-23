'use client';

import { usePathname } from 'next/navigation';
import Header from './Header';
import Sidebar from './Sidebar';
import SelectBookButton from './SelectBookButton';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  
  // Don't show layout on login page
  if (pathname === '/login') {
    return <>{children}</>;
  }

  return (
    <>
      <Header />
      <div className="min-h-screen bg-background flex pt-20">
        <Sidebar />
        <main className="flex-1 lg:ml-64">
          <div className="page-enter">
            {children}
          </div>
        </main>
        <SelectBookButton />
      </div>
    </>
  );
}
