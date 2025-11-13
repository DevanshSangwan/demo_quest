import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/api/generated/types.gen';

interface AuthStoreState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

const STORAGE_KEY = 'tonequest-auth';

export const useAuthStore = create<AuthStoreState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: true, // Start as true until we check auth state
      setUser: (user) => set({ user }),
      setToken: (token) => {
        set({ token });
        // Also update localStorage manually for immediate persistence
        if (token) {
          const stored = localStorage.getItem(STORAGE_KEY);
          if (stored) {
            try {
              const parsed = JSON.parse(stored);
              parsed.state.token = token;
              localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
            } catch {
              // Ignore parse errors
            }
          }
        }
      },
      setLoading: (loading) => set({ isLoading: loading }),
      logout: () => {
        set({ user: null, token: null });
        localStorage.removeItem(STORAGE_KEY);
      },
    }),
    {
      name: STORAGE_KEY,
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);