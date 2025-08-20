import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes that don't require authentication
  const publicRoutes = ['/login'];

  // Check if the current route is public
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  // Get the session flag from cookies (simple session check)
  const isLoggedIn = request.cookies.get('user_session')?.value === 'true';

  // If trying to access a protected route without being logged in
  if (!isPublicRoute && !isLoggedIn) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If trying to access login page while already logged in
  if (isPublicRoute && isLoggedIn && pathname === '/login') {
    return NextResponse.redirect(new URL('/upload', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
