'use client';

import { useState } from 'react';
import axios from 'axios';

export default function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:5001/api/login', { username, password });
      const token = res.data.token;
      localStorage.setItem('token', token);
      onLogin(token);
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <div className="bg-white p-6 rounded-xl shadow-md w-96 space-y-4">
        <h2 className="text-xl font-bold text-center">Security Dashboard Login</h2>
        <input
          type="text"
          placeholder="Username"
          className="w-full px-4 py-2 border rounded-md"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full px-4 py-2 border rounded-md"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Login
        </button>
      </div>
    </div>
  );
}
