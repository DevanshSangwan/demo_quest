import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getGlobalLeaderboard,
  getRelativeLeaderboard,
  updateScore,
} from '@/api/services/leaderboardService';
import type { ScoreUpdate } from '@/api/generated/types.gen';

export const GLOBAL_LEADERBOARD_QUERY_KEY = ['leaderboard', 'global'];
export const RELATIVE_LEADERBOARD_QUERY_KEY = ['leaderboard', 'relative'];

export const useGlobalLeaderboard = () => {
  return useQuery({
    queryKey: GLOBAL_LEADERBOARD_QUERY_KEY,
    queryFn: getGlobalLeaderboard,
    staleTime: 60_000,
  });
};

export const useRelativeLeaderboard = () => {
  return useQuery({
    queryKey: RELATIVE_LEADERBOARD_QUERY_KEY,
    queryFn: getRelativeLeaderboard,
    staleTime: 30_000,
  });
};

export const useUpdateScore = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scoreUpdate: ScoreUpdate) => updateScore(scoreUpdate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GLOBAL_LEADERBOARD_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: RELATIVE_LEADERBOARD_QUERY_KEY });
    },
  });
};