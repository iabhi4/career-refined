import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
export function middleware(request: NextRequest) {
  const isOnboarded = request.cookies.get('is_onboarded')?.value === 'true';
  const token = request.cookies.get('access_token');
    // Use same cookie name

  if (!token && (
    request.nextUrl.pathname.startsWith('/onboarding') ||
    request.nextUrl.pathname.startsWith('/dashboard')
  )) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }
  else if (isOnboarded && (
    request.nextUrl.pathname.startsWith('/onboarding')
  )) {
    return NextResponse.redirect(new URL('/profile', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/onboarding/:path*', '/dashboard/:path*'],
};