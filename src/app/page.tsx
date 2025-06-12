'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard page
    router.push('/dashboard');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Loading Koda Dashboard...</h1>
        <p className="mt-4">Redirecting to Kubernetes Operations & Development Assistant</p>
      </div>
    </div>
  );
}