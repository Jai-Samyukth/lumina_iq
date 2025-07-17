'use client';

import { useEffect } from 'react';

export default function DataCleaner() {
  useEffect(() => {
    // Clear all data when the app loads
    const clearAllData = () => {
      if (typeof window === 'undefined') return;
      
      // Clear localStorage
      localStorage.clear();
      
      // Clear sessionStorage
      sessionStorage.clear();
      
      // Clear all cookies
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
      }
    };

    clearAllData();
  }, []);

  return null; // This component doesn't render anything
}
