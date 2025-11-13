// src/App.tsx
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppShell } from '@/components/layout/AppShell';
import { HomePage } from '@/pages/HomePage';
import { LoginPage } from '@/pages/LoginPage';
import { LeaderboardPage } from '@/pages/LeaderboardPage';
import { AnsweringPage } from '@/pages/AnsweringPage';
import { UserInfoPage } from '@/pages/UserInfoPage';

const router = createBrowserRouter([
  {
    path: '/auth',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <HomePage /> },
          { path: 'leaderboard', element: <LeaderboardPage /> },
          { path: 'answer', element: <AnsweringPage /> },
          { path: 'user', element: <UserInfoPage /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
