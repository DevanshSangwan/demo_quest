import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { auth } from '@/firebaseConfig';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/authStore';

const copy = {
  login: {
    title: 'Log in to ToneQuest',
    description:
      "Access your personalized dashboard, keep answering prompts, and watch your writing score climb.",
    actionLabel: 'Log in with Google',
  },
  signup: {
    title: 'Create your ToneQuest account',
    description:
      'Signing up takes seconds—use the same Google account you rely on every day and start improving your writing immediately.',
    actionLabel: 'Sign up with Google',
  },
};

export const LoginPage = () => {
  const navigate = useNavigate();
  const { user, isLoading } = useAuthStore();
  const [mode, setMode] = useState<'login' | 'signup'>('login');

  useEffect(() => {
    if (!isLoading && user) {
      navigate('/', { replace: true });
    }
  }, [isLoading, user, navigate]);

  const handleGoogleAuth = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error('Authentication failed:', error);
    }
  };

  const content = copy[mode];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto flex min-h-screen flex-col items-center justify-center px-4 py-16 text-white">
        <div className="mb-8 flex gap-4 rounded-full bg-white/10 p-1 backdrop-blur-sm">
          <Button
            variant={mode === 'login' ? 'default' : 'ghost'}
            className="rounded-full px-6 py-2 text-sm font-semibold"
            onClick={() => setMode('login')}
          >
            Log In
          </Button>
          <Button
            variant={mode === 'signup' ? 'default' : 'ghost'}
            className="rounded-full px-6 py-2 text-sm font-semibold"
            onClick={() => setMode('signup')}
          >
            Sign Up
          </Button>
        </div>

        <div className="max-w-xl rounded-3xl bg-white/10 p-10 shadow-2xl backdrop-blur">
          <h1 className="text-4xl font-bold tracking-tight">{content.title}</h1>
          <p className="mt-4 text-lg text-slate-200">{content.description}</p>

          <Button
            onClick={handleGoogleAuth}
            size="lg"
            className="mt-8 w-full rounded-full text-base font-semibold"
          >
            {content.actionLabel}
          </Button>

          <p className="mt-6 text-center text-sm text-slate-300">
            ToneQuest uses your Google account to authenticate and keep your progress in sync across
            devices. Your data stays private and secure.
          </p>
        </div>
      </div>
    </div>
  );
};