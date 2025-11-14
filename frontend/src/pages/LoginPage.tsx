import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { useAuthStore } from '@/store/authStore';
import { signup, login } from '@/api/services/authService';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

const signupSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  displayName: z.string().optional(),
});

type LoginFormValues = z.infer<typeof loginSchema>;
type SignupFormValues = z.infer<typeof signupSchema>;

export const LoginPage = () => {
  const navigate = useNavigate();
  const { user, isLoading, setUser, setToken } = useAuthStore();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // useEffect(() => {
  //   // if (!isLoading && user) {
  //   //   navigate('/', { replace: true });
  //   // }
  // }, [isLoading, user, navigate]);

  const loginForm = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const signupForm = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: '',
      password: '',
      displayName: '',
    },
  });

  const handleLogin = async (values: LoginFormValues) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await login(values);
      setUser(response.user);
      setToken(response.token);
      navigate('/', { replace: true });
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSignup = async (values: SignupFormValues) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await signup({
        email: values.email,
        password: values.password,
        displayName: values.displayName || null,
      });
      setUser(response.user);
      setToken(response.token);
      navigate('/', { replace: true });
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Signup failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto flex min-h-screen flex-col items-center justify-center px-4 py-16 text-white">
        <div className="mb-8 flex gap-4 rounded-full bg-white/10 p-1 backdrop-blur-sm">
          <Button
            variant={mode === 'login' ? 'default' : 'ghost'}
            className="rounded-full px-6 py-2 text-sm font-semibold"
            onClick={() => {
              setMode('login');
              setError(null);
              loginForm.reset();
              signupForm.reset();
            }}
          >
            Log In
          </Button>
          <Button
            variant={mode === 'signup' ? 'default' : 'ghost'}
            className="rounded-full px-6 py-2 text-sm font-semibold"
            onClick={() => {
              setMode('signup');
              setError(null);
              loginForm.reset();
              signupForm.reset();
            }}
          >
            Sign Up
          </Button>
        </div>

        <div className="w-full max-w-xl rounded-3xl bg-white/10 p-10 shadow-2xl backdrop-blur">
          <h1 className="text-4xl font-bold tracking-tight">
            {mode === 'login' ? 'Log in to ToneQuest' : 'Create your ToneQuest account'}
          </h1>
          <p className="mt-4 text-lg text-slate-200">
            {mode === 'login'
              ? 'Access your personalized dashboard, keep answering prompts, and watch your writing score climb.'
              : 'Signing up takes seconds—start improving your writing immediately.'}
          </p>

          {error && (
            <div className="mt-6 rounded-lg border border-red-500/50 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          {mode === 'login' && (
            <Form {...loginForm}>
              <form onSubmit={loginForm.handleSubmit(handleLogin)} className="mt-8 space-y-6">
                <FormField
                  control={loginForm.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Email</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="you@example.com"
                          className="bg-white/5 text-white placeholder:text-slate-400"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={loginForm.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="Enter your password"
                          className="bg-white/5 text-white placeholder:text-slate-400"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="submit"
                  size="lg"
                  className="w-full rounded-full text-base font-semibold"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Logging in...' : 'Log In'}
                </Button>
              </form>
            </Form>
          ) }
          { mode=='signup' && (
            <Form {...signupForm}>
              <form onSubmit={signupForm.handleSubmit(handleSignup)} className="mt-8 space-y-6">
                <FormField
                  control={signupForm.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Email</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="you@example.com"
                          className="bg-white/5 text-white placeholder:text-slate-400"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={signupForm.control}
                  name="displayName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Display Name (Optional)</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          placeholder="Your name"
                          className="bg-white/5 text-white placeholder:text-slate-400"
                          {...field}
                          // value={field.value || ''}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={signupForm.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="At least 6 characters"
                          className="bg-white/5 text-white placeholder:text-slate-400"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="submit"
                  size="lg"
                  className="w-full rounded-full text-base font-semibold"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Creating account...' : 'Sign Up'}
                </Button>
              </form>
            </Form>
          )}

          <p className="mt-6 text-center text-sm text-slate-300">
            Your data stays private and secure. We use Firebase Authentication to protect your
            account.
          </p>
        </div>
      </div>
    </div>
  );
};
