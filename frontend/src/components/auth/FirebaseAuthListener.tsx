import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { getCurrentUser } from '@/api/services/authService';

/**
 * Component that checks authentication state on app load
 * by verifying the stored token with the backend API
 */
export const FirebaseAuthListener = () => {
  useEffect(() => {
    const checkAuthState = async () => {
      const { token } = useAuthStore.getState();
      
      // If no token is stored, user is not authenticated
      if (!token) {
        useAuthStore.getState().setLoading(false);
        return;
      }

      // Verify token by fetching current user profile
      try {
        const user = await getCurrentUser();
        useAuthStore.getState().setUser(user);
        // Token is still valid, keep it
      } catch (error) {
        // Token is invalid or expired, clear auth state
        console.error('Token verification failed:', error);
        useAuthStore.getState().setUser(null);
        useAuthStore.getState().setToken(null);
      } finally {
        useAuthStore.getState().setLoading(false);
      }
    };

    checkAuthState();
  }, []); // Empty dependency array ensures this runs only once on mount

  return null; // This component does not render anything
};