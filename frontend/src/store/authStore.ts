import { create } from 'zustand';
import { User } from 'firebase/auth'; // We will import the real type later, but this is the intent

interface AuthStoreState {
  user: User | null; // The Firebase User object
  token: string | null; // The Firebase ID Token (JWT)
  isLoading: boolean; // True on initial load, false after auth state is determined
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStoreState>((set) => ({
  user: null,
  token: null,
  isLoading: true, // Default to true until Firebase initializes
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setLoading: (loading) => set({ isLoading: loading }),
}));