'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { User, Lock, AlertCircle, Eye, EyeOff } from 'lucide-react';
import Image from 'next/image';
import Header from '@/components/Header';

export default function LoginPage() {
  const [username, setUsername] = useState('vsbec');
  const [password, setPassword] = useState('vsbec');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/about');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      router.push('/about');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="min-h-screen bg-background flex">
        {/* Left Column - Image (60%) */}
        <div className="hidden lg:flex lg:w-3/5 relative">
          <Image
            src="/pexels-cottonbro-4153146.jpg"
            alt="Learning environment"
            fill
            className="object-cover"
            priority
            sizes="(max-width: 1024px) 0vw, 60vw"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20" />
        </div>

        {/* Right Column - Login Form (40%) */}
        <div className="w-full lg:w-2/5 flex items-center justify-center p-8 lg:p-12">
          <div className="w-full max-w-md space-y-8">
            {/* Header */}
            <div className="text-center">
              <h1 className="text-4xl font-bold text-text font-display mb-2">
                Welcome to LuminaIQ-AI
              </h1>
              <p className="text-text-secondary text-lg">
                All in one learning software
              </p>
            </div>

            {/* Login Form */}
            <div className="bg-card-bg rounded-2xl shadow-xl p-8 border border-border">
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                    <span className="text-red-700 dark:text-red-400 text-sm">{error}</span>
                  </div>
                )}

                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-text mb-2">
                    Username
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <User className="h-5 w-5 text-text-secondary" />
                    </div>
                    <input
                      id="username"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      className="block w-full pl-10 pr-3 py-3 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-colors bg-background text-text placeholder-text-secondary"
                      placeholder="Enter your username"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-text mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-text-secondary" />
                    </div>
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="block w-full pl-10 pr-12 py-3 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-colors bg-background text-text placeholder-text-secondary"
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5 text-text-secondary hover:text-text transition-colors" />
                      ) : (
                        <Eye className="h-5 w-5 text-text-secondary hover:text-text transition-colors" />
                      )}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full btn-primary py-3 px-4 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {loading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Logging in...</span>
                    </div>
                  ) : (
                    'Login'
                  )}
                </button>

                {/* Forgot Password Link */}
                <div className="text-center">
                  <a href="#" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    Forgot Password?
                  </a>
                </div>
              </form>
            </div>

            {/* Sign up option */}
            <div className="text-center mt-8">
              <p className="text-text-secondary">
                Don't have an account?{' '}
                <a href="#" className="text-primary hover:text-primary/80 font-medium transition-colors">
                  Sign up
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
