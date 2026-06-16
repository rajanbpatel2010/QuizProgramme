"use client";

import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-pulse"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-purple-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-pulse delay-1000"></div>

      <div className="relative z-10 w-full max-w-4xl text-center space-y-8">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
          Master Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Tech Stack</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
          Take the ultimate role-based IT skills assessment. Challenge yourself across 10 specialized domains with dynamic AI feedback.
        </p>

        <div className="pt-8">
          <Link href="/login" className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-indigo-600 rounded-full overflow-hidden transition-transform transform hover:scale-105 hover:shadow-[0_0_40px_rgba(79,70,229,0.5)]">
            <span className="absolute inset-0 w-full h-full -mt-1 rounded-lg opacity-30 bg-gradient-to-b from-transparent via-transparent to-black"></span>
            <span className="relative flex items-center gap-2">
              Start Assessment
              <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </span>
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500 font-mono">
          <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">.NET / C#</div>
          <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">ReactJS / Angular</div>
          <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">SQL Server / SSRS</div>
          <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">Azure / Agentic AI</div>
        </div>
      </div>
    </div>
  );
}
