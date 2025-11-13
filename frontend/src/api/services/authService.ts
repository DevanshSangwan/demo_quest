import { axiosInstance } from '@/api/axiosInstance';
import type { AuthResponse, UserLogin, UserSignup } from '@/api/generated/types.gen';

/**
 * Sign up a new user with email and password
 */
export const signup = async (userData: UserSignup): Promise<AuthResponse> => {
  const { data } = await axiosInstance.post<AuthResponse>('/api/v1/auth/signup', userData);
  return data;
};

/**
 * Log in an existing user with email and password
 */
export const login = async (userData: UserLogin): Promise<AuthResponse> => {
  const { data } = await axiosInstance.post<AuthResponse>('/api/v1/auth/login', userData);
  return data;
};

/**
 * Get current user profile
 */
export const getCurrentUser = async (): Promise<import('@/api/generated/types.gen').User> => {
  const { data } = await axiosInstance.get<import('@/api/generated/types.gen').User>('/api/v1/auth/me');
  return data;
};

