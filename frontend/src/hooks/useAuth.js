import { useState, useEffect } from 'react';
import { getAuthToken } from '../services/api';

// Simple authentication hook for the TodoFlow application
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated by checking for token in localStorage
    const token = getAuthToken();
    const userId = localStorage.getItem('user_id');
    const userEmail = localStorage.getItem('user_email');
    
    if (token && userId) {
      // In a real implementation, you would decode the token or make an API call to get user info
      setIsAuthenticated(true);
      setUser({ 
        id: userId, 
        email: userEmail || 'user@example.com' 
      });
    } else {
      setIsAuthenticated(false);
      setUser(null);
    }
    
    setLoading(false);
  }, []);

  // Mock logout function - in a real app, this would call the auth API
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    setIsAuthenticated(false);
    setUser(null);
  };

  return { 
    isAuthenticated, 
    currentUser: user, 
    user, 
    loading, 
    logout 
  };
};