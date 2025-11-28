import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { fetchCurrentQuestion, submitAnswer } from "@/api/services/evaluationService";

// Type definitions (inline to avoid runtime import issues)
type QuestionPayload = {
  id: string;
  question_text: string;
  is_last_question: boolean;
};

type QuestionCompletedPayload = {
  status: string;
  message: string;
};

const getScoreColor = (score: number): string => {
  if (score < 40) return "#ef4444";
  if (score < 60) return "#f97316";
  if (score < 80) return "#f59e0b";
  return "#22c55e";
};

export const AnsweringPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [answerText, setAnswerText] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastScore, setLastScore] = useState<number | null>(null);
  const [toneFeedback, setToneFeedback] = useState<string | null>(null);
  const [grammarIssues, setGrammarIssues] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const questionQuery = useQuery({
    queryKey: ["evaluation", "currentQuestion"],
    queryFn: fetchCurrentQuestion,
  });

  const submitMutation = useMutation({
    mutationFn: submitAnswer,
    onSuccess: (data) => {
      setLastScore(data.score);
      setToneFeedback(data.tone_feedback);
      setGrammarIssues(data.grammar_issues || []);
      setSuggestions(data.suggestions);
      setShowFeedback(true);
      setHasSubmitted(true);
    },
  });

  const handleSubmit = () => {
    const data = questionQuery.data;
    if (!data || "status" in data || !answerText.trim()) {
      return;
    }
    submitMutation.mutate({
      question_id: data.id,
      answer_text: answerText.trim(),
    });
  };

  const handleLoadAnotherQuestion = () => {
    setAnswerText("");
    setShowFeedback(false);
    setLastScore(null);
    setToneFeedback(null);
    setGrammarIssues([]);
    setSuggestions(null);
    setHasSubmitted(false);
    queryClient.invalidateQueries({ queryKey: ["evaluation", "currentQuestion"] });
  };

  const data = questionQuery.data;
  const isCompleted = data && "status" in data;
  const question = !isCompleted ? (data as QuestionPayload) : null;

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <h1 className="text-3xl font-bold tracking-tight">Answer a Prompt</h1>
        <p className="text-muted-foreground">
          Craft a thoughtful response to the prompt below. When you submit, we&apos;ll evaluate your
          answer against high-quality examples and update your leaderboard position automatically.
        </p>
      </header>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        {questionQuery.isLoading && (
          <p className="text-sm text-muted-foreground">Loading your next question...</p>
        )}

        {questionQuery.isError && (
          <div className="rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
            We had trouble loading a question. Try again in a moment.
          </div>
        )}

        {isCompleted && (
          <div className="space-y-4 text-center">
            <h2 className="text-2xl font-semibold text-primary">
              {(data as QuestionCompletedPayload).message}
            </h2>
            <Button
              onClick={() => navigate("/")}
              className="bg-blue-500 text-white hover:bg-blue-600"
            >
              Exit to Home
            </Button>
          </div>
        )}

        {question && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
              <span>Question Number: {question.id}</span>
            </div>
            <h2 className="text-xl font-semibold">{question.question_text}</h2>
            <textarea
              value={answerText}
              onChange={(event) => setAnswerText(event.target.value)}
              placeholder="Write your answer here..."
              className="min-h-[200px] w-full resize-y rounded-xl border border-border bg-background px-4 py-3 text-base shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
              disabled={hasSubmitted}
            />
            <div className="flex flex-wrap items-center gap-4">
              <Button
                onClick={handleSubmit}
                disabled={hasSubmitted || submitMutation.isPending || !answerText.trim()}
                className="bg-blue-500 text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitMutation.isPending ? "Evaluating..." : "Submit Answer"}
              </Button>
              {hasSubmitted &&
                (question.is_last_question ? (
                  <Button
                    onClick={() => navigate("/")}
                    className="bg-green-500 text-white hover:bg-green-600"
                    type="button"
                  >
                    Finish Session
                  </Button>
                ) : (
                  <Button
                    onClick={handleLoadAnotherQuestion}
                    className="bg-blue-500 text-white hover:bg-blue-600"
                    type="button"
                  >
                    Next Question
                  </Button>
                ))}
            </div>
          </div>
        )}
      </section>

      {submitMutation.isPending && (
        <section className="rounded-2xl border border-primary/40 bg-primary/5 p-6 animate-pulse">
          <div className="flex items-center gap-3">
            <svg className="h-5 w-5 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-lg font-medium text-primary">ToneQuest AI is reviewing your answer...</p>
          </div>
        </section>
      )}

      {showFeedback && lastScore !== null && (
        <section className="rounded-2xl border border-primary/40 bg-primary/5 p-6 space-y-4">
          <div className="relative flex items-center justify-center">
            <svg className="w-32 h-32 -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="#e5e7eb"
                strokeWidth="10"
                fill="none"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke={getScoreColor(lastScore)}
                strokeWidth="10"
                fill="none"
                strokeDasharray={2 * Math.PI * 56}
                strokeDashoffset={2 * Math.PI * 56 - (lastScore / 100) * 2 * Math.PI * 56}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 1s ease-out' }}
              />
            </svg>
            <div className="absolute">
              <p className="text-3xl font-bold" style={{ color: getScoreColor(lastScore) }}>
                {Math.round(lastScore)}
              </p>
            </div>
          </div>

          {toneFeedback && (
            <div>
              <p className="text-sm font-bold">Tone Feedback</p>
              <p className="mt-1 text-sm text-foreground">{toneFeedback}</p>
            </div>
          )}

          {grammarIssues.length > 0 && (
            <div>
              <p className="text-sm font-bold">Grammar Issues</p>
              <ul className="mt-1 list-disc list-inside space-y-1">
                {grammarIssues.map((issue, idx) => (
                  <li key={idx} className="text-sm text-foreground">{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {suggestions && (
            <div>
              <p className="text-sm font-bold">Suggestions</p>
              <p className="mt-1 text-sm text-foreground">{suggestions}</p>
            </div>
          )}
        </section>
      )}
    </div>
  );
};

