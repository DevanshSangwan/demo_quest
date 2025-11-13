import { axiosInstance } from '@/api/axiosInstance';
import type { LeaderboardEntry, ScoreUpdate } from '@/api/generated/types.gen';

export interface RelativeLeaderboardResponse {
  rank: number;
  entries: LeaderboardEntry[];
}

export const getGlobalLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  const { data } = await axiosInstance.get<LeaderboardEntry[]>('/api/v1/leaderboard', {
    params: { limit: 10 },
  });
  return data;
};

export const getRelativeLeaderboard = async (): Promise<RelativeLeaderboardResponse> => {
  const { data } = await axiosInstance.get<RelativeLeaderboardResponse>('/api/v1/leaderboard/around_me');
  return data;
};

export const updateScore = async (scoreUpdate: ScoreUpdate): Promise<void> => {
  await axiosInstance.post('/api/v1/leaderboard/update', scoreUpdate);
};