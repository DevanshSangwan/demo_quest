import { axiosInstance } from '@/api/axiosInstance';
import type { User } from '@/api/generated/types.gen';

export const fetchCurrentUser = async (): Promise<User> => {
  const { data } = await axiosInstance.get<User>('/api/v1/auth/me');
  return data;
};

export interface ScoreHistoryEntry {
  question_id: number;
  score: number;
  submitted_at: string;
}

export interface RankHistoryEntry {
  date: string;
  rank: number;
}

export const fetchUserScoreHistory = async (): Promise<ScoreHistoryEntry[]> => {
  const { data } = await axiosInstance.get<ScoreHistoryEntry[]>('/api/v1/user/score-history');
  return data;
};

export const fetchUserRankHistory = async (): Promise<RankHistoryEntry[]> => {
  const { data } = await axiosInstance.get<RankHistoryEntry[]>('/api/v1/leaderboard/rank-history');
  return data;
};

