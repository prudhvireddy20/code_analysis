'use client';

import { useEffect, useState } from 'react';
import Dashboard from '@/components/Dashboard';
import Login from '@/components/Login';

export default function Home() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem('token');
    setToken(t);
  }, []);

  return (
    <main className="min-h-screen bg-gray-100">
      {token ? <Dashboard token={token} /> : <Login onLogin={setToken} />}
    </main>
  );
}
