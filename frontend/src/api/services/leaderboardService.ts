import { axiosInstance } from '@/api/axiosInstance';
// Import your generated types. The names will depend on your backend's Pydantic models.
import { LeaderboardEntry, ScoreUpdate } from '@/api/generated/types.gen'; 

/**
 * Fetches the entire leaderboard.
 */
export const getLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  const { data } = await axiosInstance.get<LeaderboardEntry[]>('/api/v1/leaderboard');
  return data;
};

/**
 * Creates a new entry in the leaderboard.
 */
export const updateScore = async (scoreUpdate: ScoreUpdate): Promise<void> => {
  await axiosInstance.post('/api/v1/leaderboard/update', scoreUpdate);
};