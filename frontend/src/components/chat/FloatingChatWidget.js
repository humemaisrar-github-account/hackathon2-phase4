import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../../services/auth';
import ChatInterface from '../chat/ChatInterface';

const FloatingChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { currentUser, isAuthenticated } = useAuth();
  const router = useRouter();

  const toggleChat = () => {
    if (!isAuthenticated) {
      // Redirect to login if not authenticated
      router.push('/auth/login');
      return;
    }
    
    setIsOpen(!isOpen);
  };

  if (!isAuthenticated) {
    return null; // Only show to authenticated users
  }

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setIsOpen(false)}></div>
      )}
      
      <div className="fixed bottom-6 right-6 z-50">
        {isOpen ? (
          <div className="w-80 h-96 bg-white rounded-lg shadow-xl flex flex-col border border-gray-200 overflow-hidden">
            <div className="bg-blue-600 text-white p-3 flex justify-between items-center">
              <h3 className="font-semibold">AI Todo Assistant</h3>
              <button 
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-gray-200 focus:outline-none"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatInterface userId={currentUser?.id} onTaskUpdate={() => {
                // Dispatch a custom event to notify the dashboard to refresh
                window.dispatchEvent(new CustomEvent('taskUpdated'));
              }} />
            </div>
          </div>
        ) : (
          <button
            onClick={toggleChat}
            className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all duration-300 transform hover:scale-105 flex items-center justify-center"
            aria-label="Open AI Chat Assistant"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </button>
        )}
      </div>
    </>
  );
};

export default FloatingChatWidget;