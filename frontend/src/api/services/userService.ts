import { axiosInstance } from '@/api/axiosInstance';
import type { User } from '@/api/generated/types.gen';

export const fetchCurrentUser = async (): Promise<User> => {
  const { data } = await axiosInstance.get<User>('/api/v1/auth/me');
  return data;
};

