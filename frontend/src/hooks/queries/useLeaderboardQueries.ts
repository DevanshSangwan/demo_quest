import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLeaderboard, createLeaderboardEntry } from '@/api/services/leaderboardService';
import { NewLeaderboardEntry } from '@/api/generated/models'; // Import generated type

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
 * Custom hook to create a new leaderboard entry.
 */
export const useCreateLeaderboardEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newEntry: NewLeaderboardEntry) => createLeaderboardEntry(newEntry),

    // On success, invalidate the leaderboard query to refetch the data
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LEADERBOARD_QUERY_KEY });
    },
  });
};