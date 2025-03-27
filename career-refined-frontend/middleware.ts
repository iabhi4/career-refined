import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: [
    '/',                         // 1) match root
    '/onboarding/:path*',
    '/dashboard/:path*',
    '/editor/:path*',
    '/profile/:path*',
    '/tracker/:path*',
  ],
};

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  const isOnboarded = request.cookies.get('is_onboarded')?.value === 'true';
  const { pathname } = request.nextUrl;

  // --- 1) If user hits the root path ---
  if (pathname === '/') {
    if (!token) {
      return NextResponse.redirect(new URL('/auth/login', request.url));
    }
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // --- 2) For other protected routes ---
  // If not authenticated => go to login
  if (!token) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  // If user is onboarded but visits /onboarding => redirect to /dashboard
  if (isOnboarded && pathname.startsWith('/onboarding')) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // If user is NOT onboarded and tries to go anywhere but /onboarding => redirect there
  if (!isOnboarded && !pathname.startsWith('/onboarding')) {
    return NextResponse.redirect(new URL('/onboarding', request.url));
  }

  // Otherwise, allow the request
  return NextResponse.next();
}