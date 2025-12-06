import { useQuery } from '@tanstack/react-query';
import { fetchUserScoreHistory, fetchUserRankHistory } from '@/api/services/userService';

export const useScoreHistory = () => {
  return useQuery({
    queryKey: ['user', 'scoreHistory'],
    queryFn: fetchUserScoreHistory,
  });
};

export const useRankHistory = () => {
  return useQuery({
    queryKey: ['user', 'rankHistory'],
    queryFn: fetchUserRankHistory,
  });
};
