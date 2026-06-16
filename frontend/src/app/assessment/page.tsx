"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

let API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
if (API_URL && !API_URL.startsWith('http')) {
  API_URL = `https://${API_URL}`;
}

export default function AssessmentPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answeredMap, setAnsweredMap] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(true);
  const [isFinished, setIsFinished] = useState(false);
  const [attemptId, setAttemptId] = useState<number | null>(null);

  useEffect(() => {
    const aid = localStorage.getItem('attemptId');
    if (aid) {
      setAttemptId(parseInt(aid));
      fetchQuestions(parseInt(aid));
    } else {
      router.push('/login');
    }
  }, []);

  const fetchQuestions = async (aid: number) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/assessment/${aid}/questions`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (res.status === 404 || res.status === 400) {
        setIsFinished(true);
        router.push('/results');
        return;
      }
      
      if (!res.ok) throw new Error('Failed to fetch questions');
      
      const data = await res.json();
      setQuestions(data.questions);
      setAnsweredMap(data.answered_map);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (answerId: number) => {
    if (questions.length === 0 || !attemptId) return;
    const currentQuestion = questions[currentIndex];
    
    // Optimistic UI update
    setAnsweredMap(prev => ({ ...prev, [currentQuestion.id]: answerId }));
    
    try {
      await fetch(`${API_URL}/assessment/${attemptId}/submit`, { 
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({
          question_id: currentQuestion.id,
          selected_answer_id: answerId
        })
      });
      
      // Auto-advance if we are not on the last question
      if (currentIndex < questions.length - 1) {
        setTimeout(() => handleNext(), 300);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const handleFinishEarly = async () => {
    if (!attemptId) return;
    if (!confirm("Are you sure you want to finish the test early?")) return;
    
    setLoading(true);
    try {
      await fetch(`${API_URL}/assessment/${attemptId}/finish`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setIsFinished(true);
      router.push('/results');
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-screen"><div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div></div>;

  if (questions.length === 0) return <div className="flex justify-center items-center h-screen text-2xl font-bold">Assessment Complete!</div>;

  const currentQuestion = questions[currentIndex];
  const selectedAnswerId = answeredMap[currentQuestion.id];
  const progressPercent = Math.round(((currentIndex + 1) / questions.length) * 100);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-3xl bg-gray-800 rounded-xl shadow-2xl p-8 transform transition-all">
        
        {/* Progress Header */}
        <div className="mb-6">
          <div className="flex justify-between text-sm font-semibold text-gray-400 mb-2">
            <span>Question {currentIndex + 1} of {questions.length}</span>
            <span>{Object.keys(answeredMap).length} Answered</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div className="bg-indigo-500 h-2.5 rounded-full transition-all duration-500" style={{ width: `${progressPercent}%` }}></div>
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
          <h2 className="text-xl font-semibold text-indigo-400">Technical Assessment</h2>
          <button 
            onClick={handleFinishEarly}
            className="px-4 py-2 bg-red-600/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-600 hover:text-white transition-colors text-sm font-medium"
          >
            Submit Test
          </button>
        </div>

        {/* Question Area */}
        <div className="mb-8 min-h-[150px]">
          <h1 className="text-2xl font-bold mb-4 leading-relaxed">{currentQuestion.question_text}</h1>
          {currentQuestion.practical_example && (
            <pre className="bg-gray-950 p-4 rounded-lg overflow-x-auto border border-gray-700 text-sm font-mono text-green-300">
              {currentQuestion.practical_example}
            </pre>
          )}
        </div>

        {/* Options */}
        <div className="space-y-4 mb-8">
          {currentQuestion.answers.map((ans: any) => (
            <button
              key={ans.id}
              onClick={() => submitAnswer(ans.id)}
              className={`w-full text-left p-4 rounded-lg transition-colors duration-200 border focus:outline-none ${
                selectedAnswerId === ans.id 
                  ? 'bg-indigo-600 border-indigo-400 ring-2 ring-indigo-500 ring-offset-2 ring-offset-gray-900' 
                  : 'bg-gray-700 hover:bg-gray-600 border-gray-600'
              }`}
            >
              {ans.answer_text}
            </button>
          ))}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-4 border-t border-gray-700">
          <button
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              currentIndex === 0 ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-gray-700 text-white hover:bg-gray-600'
            }`}
          >
            Previous
          </button>

          {currentIndex < questions.length - 1 ? (
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 font-medium transition-colors"
            >
              Next Skip
            </button>
          ) : (
             <button
              onClick={handleFinishEarly}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 font-medium transition-colors shadow-[0_0_15px_rgba(79,70,229,0.5)]"
            >
              Finish Assessment
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
