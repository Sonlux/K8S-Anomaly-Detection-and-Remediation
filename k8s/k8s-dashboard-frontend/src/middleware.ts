import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Define paths that don't require authentication
const publicPaths = ["/login", "/api/", "/_next/", "/images/", "/favicon.ico"];

// Function to check if the path is public
const isPublicPath = (path: string): boolean => {
  return publicPaths.some((publicPath) => path.startsWith(publicPath));
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow access to public paths without authentication
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // Check for auth token in cookies
  const authToken = request.cookies.get("auth_token")?.value;

  // If no auth token is found, redirect to login page
  if (!authToken) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  // User is authenticated, allow access to protected route
  return NextResponse.next();
}

// Configure middleware to run on specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * 1. /api routes (API routes)
     * 2. /_next (Next.js internals)
     * 3. /fonts, /images (static files)
     * 4. /favicon.ico, /sitemap.xml (static files)
     */
    "/((?!api|_next|fonts|images|favicon.ico|sitemap.xml).*)",
  ],
};
