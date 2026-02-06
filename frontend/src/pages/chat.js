import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import ChatInterface from '../components/chat/ChatInterface';

const ChatPage = () => {
  const router = useRouter();
  const { user, isAuthenticated, loading } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Redirect happens in useEffect
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">AI Todo Assistant</h1>
        <p className="text-gray-600 mb-6">Manage your tasks with natural language commands</p>
        
        <div className="h-[600px] flex flex-col">
          <ChatInterface userId={user?.id} />
        </div>
        
        <div className="mt-8 bg-blue-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-blue-800 mb-2">How to use the AI Assistant</h2>
          <ul className="list-disc pl-5 space-y-1 text-blue-700">
            <li>Add tasks: "Add a task to buy groceries"</li>
            <li>List tasks: "Show me my pending tasks" or "What have I completed?"</li>
            <li>Complete tasks: "Mark task 1 as complete" or "Finish the meeting task"</li>
            <li>Delete tasks: "Delete the old task" or "Remove task 2"</li>
            <li>Update tasks: "Change task 1 to 'Call mom tonight'"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;