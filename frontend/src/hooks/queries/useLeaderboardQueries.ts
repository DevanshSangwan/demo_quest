import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLeaderboard, updateScore } from '@/api/services/leaderboardService';
import { ScoreUpdate } from '@/api/generated/types.gen'; // Import generated type

// Centralize query keys
export const LEADERBOARD_QUERY_KEY = ['leaderboard'];

/**
 * Custom hook to fetch the leaderboard.
 */
export const useGetLeaderboard = () => {
  return useQuery({
    queryKey: LEADERBOARD_QUERY_KEY,
    queryFn: getLeaderboard, // Pass the service function directly
  });
};

/**
 * Custom hook to update a user's score.
 */
export const useUpdateScore = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scoreUpdate: ScoreUpdate) => updateScore(scoreUpdate),

    // On success, invalidate the leaderboard query to refetch the data
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LEADERBOARD_QUERY_KEY });
    },
  });
};