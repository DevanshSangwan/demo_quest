import { axiosInstance } from '@/api/axiosInstance';

export interface QuestionPayload {
  id: string;
  prompt_text: string;
  category: string;
  difficulty: string;
  reference_answers: string[];
}

export interface EvaluationResult {
  submission_id: string;
  similarity_score: number;
  best_match_answer: string;
  leaderboard: {
    average_score: number;
    best_score: number;
    submission_count: number;
  };
}

export const fetchNextQuestion = async (): Promise<QuestionPayload> => {
  const { data } = await axiosInstance.get<QuestionPayload>('/api/v1/questions/next');
  return data;
};

export const submitAnswer = async (payload: {
  question_id: string;
  answer_text: string;
}): Promise<EvaluationResult> => {
  const { data } = await axiosInstance.post<EvaluationResult>('/api/v1/evaluate_answer', payload);
  return data;
};

