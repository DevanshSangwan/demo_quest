import { axiosInstance } from '@/api/axiosInstance';
// Import your generated types. The names will depend on your backend's Pydantic models.
import { LeaderboardEntry, NewLeaderboardEntry } from '@/api/generated/models'; 

/**
 * Fetches the entire leaderboard.
 */
export const getLeaderboard = async (): Promise<LeaderboardEntry> => {
  // The generated client may also provide this function, but this is a
  // robust way to use the central axios instance.
  // If using the generated client:
  // import { DefaultService } from '@/api/generated';
  // return DefaultService.getLeaderboardV1LeaderboardGet();
  // If using axiosInstance directly:
  const { data } = await axiosInstance.get<LeaderboardEntry>('/v1/leaderboard');
  return data;
};

/**
 * Creates a new entry in the leaderboard.
 */
export const createLeaderboardEntry = async (newEntry: NewLeaderboardEntry): Promise<LeaderboardEntry> => {
  const { data } = await axiosInstance.post<LeaderboardEntry>('/v1/leaderboard', newEntry);
  return data;
};