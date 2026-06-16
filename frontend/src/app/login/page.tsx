"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

let API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
if (API_URL && !API_URL.startsWith('http')) {
  API_URL = `https://${API_URL}`;
}

const ROLES = [
  "Fresher Software Developer",
  "Experienced Software Developer",
  "Advanced Software Developer",
  "Technical Lead",
  "Technical Architect",
  "Project Manager",
  "Program Manager",
];

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState(ROLES[0]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!isLogin) {
        // Register
        const regRes = await fetch(`${API_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, name, role })
        });
        if (!regRes.ok) {
          const data = await regRes.json();
          throw new Error(data.detail || 'Registration failed');
        }
      }

      // Login
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const loginRes = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      });

      if (!loginRes.ok) throw new Error('Invalid Credentials');

      const loginData = await loginRes.json();
      localStorage.setItem('token', loginData.access_token);
      
      // Start Assessment immediately
      const startRes = await fetch(`${API_URL}/assessment/start`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${loginData.access_token}` }
      });
      
      if (!startRes.ok) throw new Error('Could not start assessment');
      const startData = await startRes.json();
      localStorage.setItem('attemptId', startData.id.toString());
      
      router.push('/assessment');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-6 text-white relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-pulse"></div>
      
      <div className="relative z-10 w-full max-w-md bg-gray-900 rounded-2xl shadow-2xl p-8 border border-gray-800">
        <h2 className="text-3xl font-extrabold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        
        {error && <div className="bg-red-500/10 border border-red-500 text-red-400 p-3 rounded-lg mb-6 text-sm text-center">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Full Name</label>
              <input type="text" required value={name} onChange={(e) => setName(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition" />
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Email Address</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition" />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Role / Experience Level</label>
              <select value={role} onChange={(e) => setRole(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition">
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          )}

          <button type="submit" disabled={loading} className="w-full py-3 mt-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg shadow-lg transition-all duration-300 disabled:opacity-50">
            {loading ? 'Processing...' : (isLogin ? 'Sign In & Start' : 'Register & Start')}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => setIsLogin(!isLogin)} className="text-indigo-400 hover:text-indigo-300 font-medium">
            {isLogin ? 'Register' : 'Sign In'}
          </button>
        </div>
        
        <div className="mt-4 text-center">
            <Link href="/" className="text-gray-600 hover:text-gray-400 text-xs">Back to Home</Link>
        </div>
      </div>
    </div>
  );
}
