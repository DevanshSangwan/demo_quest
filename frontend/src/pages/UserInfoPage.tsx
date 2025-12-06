import { useQuery } from "@tanstack/react-query";
import { fetchCurrentUser } from "@/api/services/userService";
import { useRelativeLeaderboard } from "@/hooks/queries/useLeaderboardQueries";
import { useScoreHistory, useRankHistory } from "@/hooks/queries/useUserQueries";
import { ScoreHistoryChart } from "@/components/charts/ScoreHistoryChart";
import { RankHistoryChart } from "@/components/charts/RankHistoryChart";

export const UserInfoPage = () => {
  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ["user", "profile"],
    queryFn: fetchCurrentUser,
  });

  const {
    data: relativeLeaderboard,
    isLoading: isRankLoading,
    isError: isRankError,
  } = useRelativeLeaderboard();

  const { data: scoreHistory, isLoading: isScoreLoading } = useScoreHistory();
  const { data: rankHistory, isLoading: isRankHistoryLoading } = useRankHistory();

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <h1 className="text-3xl font-bold tracking-tight">Your ToneQuest Profile</h1>
        <p className="text-muted-foreground">
          Review the information linked to your account, including activity metrics and current
          leaderboard placement.
        </p>
      </header>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading your profile...</p>
        ) : isError ? (
          <p className="text-sm text-destructive">
            We couldn&apos;t load your profile right now. Please try again later.
          </p>
        ) : profile ? (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold">Account Details</h2>
              <dl className="mt-3 space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center justify-between">
                  <dt className="font-medium text-foreground">Display name</dt>
                  <dd>{profile.displayName || "Not set"}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="font-medium text-foreground">Email address</dt>
                  <dd>{profile.email}</dd>
                </div>
              </dl>
            </div>
            <div>
              <h3 className="text-lg font-semibold">Activity</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Total submissions:{" "}
                <span className="font-semibold text-foreground">{profile.totalSubmissions}</span>
              </p>
            </div>
          </div>
        ) : null}
      </section>

      <section className="rounded-2xl border border-dashed border-border bg-background p-6">
        <h2 className="text-xl font-semibold">Current Leaderboard Placement</h2>
        {isRankLoading ? (
          <p className="mt-2 text-sm text-muted-foreground">Checking your current rank...</p>
        ) : isRankError || !relativeLeaderboard ? (
          <p className="mt-2 text-sm text-muted-foreground">
            Submit an answer to join the leaderboard and start tracking your rank.
          </p>
        ) : (
          <div className="mt-3 space-y-1 text-sm text-muted-foreground">
            <p>
              You are currently ranked{" "}
              <span className="font-semibold text-foreground">
                #{relativeLeaderboard.rank}
              </span>{" "}
              overall.
            </p>
            <p>
              The leaderboard page highlights the five writers ahead of you and four writers just
              behind—keep submitting polished responses to climb higher!
            </p>
          </div>
        )}
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Your Progress Over Time</h2>
        {isScoreLoading || isRankHistoryLoading ? (
          <p className="text-sm text-muted-foreground">Loading your progress data...</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            <ScoreHistoryChart data={scoreHistory || []} />
            <RankHistoryChart data={rankHistory || []} />
          </div>
        )}
      </section>
    </div>
  );
};

