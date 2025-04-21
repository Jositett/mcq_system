import React from 'react';

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] bg-gradient-to-br from-blue-50 to-blue-100 p-8 text-center">
      <h1 className="text-4xl md:text-5xl font-bold mb-4 text-blue-800 drop-shadow">Welcome to the MCQ System</h1>
      <p className="text-lg md:text-xl text-blue-700 mb-8">Please login or register to continue.</p>
      {/* Optionally, add login/register buttons here if you want prominent CTAs */}
    </div>
  );
}
