import { useEffect } from 'react';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '@/firebaseConfig';
import { useAuthStore } from '@/store/authStore';

export const FirebaseAuthListener = () => {
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user: User | null) => {
      if (user) {
        // User is signed in
        try {
          const idToken = await user.getIdToken();
          useAuthStore.getState().setUser(user);
          useAuthStore.getState().setToken(idToken);
        } catch (error) {
          console.error('Error getting ID token:', error);
          // Handle error: perhaps log out the user
          useAuthStore.getState().setUser(null);
          useAuthStore.getState().setToken(null);
        }
      } else {
        // User is signed out
        useAuthStore.getState().setUser(null);
        useAuthStore.getState().setToken(null);
      }
      // Set loading to false once the auth state is determined
      useAuthStore.getState().setLoading(false);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []); // Empty dependency array ensures this runs only once on mount

  return null; // This component does not render anything
};