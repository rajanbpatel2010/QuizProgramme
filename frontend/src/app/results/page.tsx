"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [enhancing, setEnhancing] = useState(false);
  const [enhancedMsg, setEnhancedMsg] = useState("");

  useEffect(() => {
    const aid = localStorage.getItem('attemptId');
    if (!aid) {
      router.push('/login');
      return;
    }

    const fetchResult = async () => {
      try {
        const res = await fetch(`${API_URL}/assessment/${aid}/result`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        if (!res.ok) throw new Error('Could not fetch results');
        const data = await res.json();
        setResult(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchResult();
  }, []);

  const handleEnhanceKnowledge = async () => {
    setEnhancing(true);
    try {
      const aid = localStorage.getItem('attemptId');
      await fetch(`${API_URL}/assessment/${aid}/enhance-knowledge`, { 
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      setEnhancedMsg("Knowledge enhancement initiated! The AI worker is finding new questions to expand your database.");
    } catch (error) {
      console.error(error);
    } finally {
      setEnhancing(false);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-screen bg-gray-900"><div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div></div>;

  if (!result) return <div className="flex justify-center items-center h-screen bg-gray-900 text-white text-2xl">Could not load results.</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-6 py-12">
      <div className="w-full max-w-4xl bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
        
        <div className="text-center mb-10 border-b border-gray-700 pb-8">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 mb-4">
            Assessment Complete!
          </h1>
          <p className="text-xl text-gray-300">
            Your Score: <span className="text-green-400 font-bold text-3xl">{result.score ?? 0}</span> / {result.total ?? 10}
          </p>
        </div>

        <div className="mb-10 bg-gray-900 p-6 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-bold mb-6 text-indigo-300 flex items-center">
            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            AI Professional Summary
          </h2>
          <div className="prose prose-invert max-w-none text-gray-300 whitespace-pre-line">
            {result.ai_summary || "No AI summary available."}
          </div>
        </div>

        <div className="flex flex-col items-center justify-center pt-6 border-t border-gray-700">
          <p className="text-gray-400 mb-4 text-center">
            Want to expand the question bank based on your performance? 
          </p>
          <button
            onClick={handleEnhanceKnowledge}
            disabled={enhancing || !!enhancedMsg}
            className={`px-8 py-3 rounded-lg font-bold transition-all duration-300 ${
              enhancing ? 'bg-indigo-800 cursor-not-allowed' : 
              enhancedMsg ? 'bg-green-600 cursor-default' : 
              'bg-indigo-600 hover:bg-indigo-500 shadow-lg hover:shadow-indigo-500/30'
            }`}
          >
            {enhancing ? 'AI Worker Running...' : 
             enhancedMsg ? 'Enhancement Active' : 
             'Enhance Knowledge Base'}
          </button>
          
          {enhancedMsg && (
            <p className="mt-4 text-green-400 font-medium animate-pulse">
              {enhancedMsg}
            </p>
          )}

          <button
            onClick={() => { localStorage.removeItem('attemptId'); router.push('/login'); }}
            className="mt-6 px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-gray-300 transition-colors"
          >
            Take Another Assessment
          </button>
        </div>

      </div>
    </div>
  );
}
