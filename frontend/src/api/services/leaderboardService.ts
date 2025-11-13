import { axiosInstance } from '@/api/axiosInstance';
import type { LeaderboardEntry, ScoreUpdate } from '@/api/generated/types.gen';

/**
 * Fetches the entire leaderboard.
 */
export const getLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  const { data } = await axiosInstance.get<LeaderboardEntry[]>('/api/v1/leaderboard');
  return data;
};

/**
 * Applies a manual score adjustment for an existing leaderboard entry.
 */
export const updateScore = async (scoreUpdate: ScoreUpdate): Promise<void> => {
  await axiosInstance.post('/api/v1/leaderboard/update', scoreUpdate);
};