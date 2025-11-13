import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
// Import your spinner component, e.g.:
// import { Spinner } from '@/lib/components/ui/spinner'; 

export const ProtectedRoute = () => {
  const { user, token, isLoading } = useAuthStore();

  // 1. Check if auth state is still loading
  if (isLoading) {
    // Render a full-page loading spinner
    return (
      <div className="flex h-screen items-center justify-center">
        {/* <Spinner size="lg" /> */}
        <p>Loading...</p> 
      </div>
    );
  }

  // 2. After loading, check if user and token are present
  if (!user || !token) {
    // Not authenticated, redirect to login
    return <Navigate to="/login" replace />;
  }

  // 3. User is authenticated, render the child route
  return <Outlet />;
};