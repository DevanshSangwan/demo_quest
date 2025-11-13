import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { fetchNextQuestion, submitAnswer } from "@/api/services/evaluationService";

export const AnsweringPage = () => {
  const navigate = useNavigate();
  const [answerText, setAnswerText] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastScore, setLastScore] = useState<number | null>(null);
  const [bestMatch, setBestMatch] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const questionQuery = useQuery({
    queryKey: ["evaluation", "question"],
    queryFn: fetchNextQuestion,
  });

  const submitMutation = useMutation({
    mutationFn: submitAnswer,
    onSuccess: (data) => {
      setLastScore(data.similarity_score);
      setBestMatch(data.best_match_answer);
      setShowFeedback(true);
      setHasSubmitted(true);
    },
  });

  const handleSubmit = () => {
    if (!questionQuery.data || !answerText.trim()) {
      return;
    }
    submitMutation.mutate({
      question_id: questionQuery.data.id,
      answer_text: answerText.trim(),
    });
  };

  const handleLoadAnotherQuestion = () => {
    setAnswerText("");
    setShowFeedback(false);
    setLastScore(null);
    setBestMatch(null);
    setHasSubmitted(false);
    questionQuery.refetch();
  };

  const question = questionQuery.data;

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

        {question && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
              <span>Question Number: {question.id}</span>
            </div>
            <h2 className="text-xl font-semibold">{question.prompt_text}</h2>
            <textarea
              value={answerText}
              onChange={(event) => setAnswerText(event.target.value)}
              placeholder="Write your answer here..."
              className="min-h-[200px] w-full resize-y rounded-xl border border-border bg-background px-4 py-3 text-base shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
            <div className="flex flex-wrap items-center gap-4">
              <Button
                onClick={handleSubmit}
                disabled={hasSubmitted || submitMutation.isPending || !answerText.trim()}
                className="disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitMutation.isPending ? "Submitting..." : "Submit Answer"}
              </Button>
              <Button
                variant="outline"
                onClick={handleLoadAnotherQuestion}
                disabled={!hasSubmitted}
                className="disabled:cursor-not-allowed disabled:opacity-50"
                type="button"
              >
                Try Another Question
              </Button>
              {hasSubmitted && (
                <Button
                  variant="ghost"
                  onClick={() => setHasSubmitted(false)}
                  type="button"
                >
                  Try Again
                </Button>
              )}
              <Button
                variant="outline"
                onClick={() => navigate("/")}
                disabled={submitMutation.isPending}
                className="disabled:cursor-not-allowed disabled:opacity-50"
                type="button"
              >
                Exit to Home
              </Button>
            </div>
          </div>
        )}
      </section>

      {showFeedback && lastScore !== null && (
        <section className="rounded-2xl border border-primary/40 bg-primary/5 p-6">
          <h3 className="text-lg font-semibold">Feedback</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Your similarity score for this submission is{" "}
            <span className="font-semibold text-primary">
              {(lastScore * 100).toFixed(1)}%
            </span>
            .
          </p>
          {bestMatch && (
            <p className="mt-4 text-sm text-muted-foreground">
              Closest example answer:
              <span className="mt-1 block rounded-lg bg-white/60 p-3 font-medium text-foreground">
                {bestMatch}
              </span>
            </p>
          )}
          <p className="mt-4 text-sm text-muted-foreground">
            Keep practicing! Each submission updates your personal ranking and helps us tailor future
            prompts to your growth.
          </p>
        </section>
      )}
    </div>
  );
};

