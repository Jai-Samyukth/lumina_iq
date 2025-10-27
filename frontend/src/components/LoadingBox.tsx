'use client';

import { Loader2 } from 'lucide-react';

interface LoadingBoxProps {
  message?: string;
  isVisible: boolean;
}

export default function LoadingBox({ message = "Please Wait a BIT", isVisible }: LoadingBoxProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-cream border-2 border-terracotta rounded-2xl p-8 text-center shadow-2xl transform transition-all duration-200">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-terracotta border-t-transparent"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader2 className="h-6 w-6 text-terracotta animate-spin" />
            </div>
          </div>
          <div>
            <h3 className="text-xl font-bold text-olive-green mb-2">{message}</h3>
            <p className="text-sm text-muted-sage">Processing your PDF...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
