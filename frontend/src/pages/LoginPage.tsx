import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { auth } from '@/firebaseConfig';
import { Button } from '@/components/ui/button';

export const LoginPage = () => {
  const handleGoogleLogin = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-8">Login</h1>
      <Button onClick={handleGoogleLogin} size="lg">
        Login with Google
      </Button>
    </div>
  );
};