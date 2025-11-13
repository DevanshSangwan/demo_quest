import { Button } from "@/components/ui/button";
import { LeaderboardTable } from "@/components/leaderboard/LeaderboardTable";
import { useGlobalLeaderboard, useRelativeLeaderboard } from "@/hooks/queries/useLeaderboardQueries";

export const LeaderboardPage = () => {
  const {
    data: globalLeaderboard,
    isLoading: isGlobalLoading,
    isError: isGlobalError,
    refetch: refetchGlobal,
  } = useGlobalLeaderboard();

  const {
    data: relativeLeaderboard,
    isLoading: isRelativeLoading,
    isError: isRelativeError,
    refetch: refetchRelative,
  } = useRelativeLeaderboard();

  return (
    <div className="space-y-12">
      <header className="space-y-3">
        <h1 className="text-3xl font-bold tracking-tight">Leaderboards</h1>
        <p className="text-muted-foreground">
          Compare your performance with the ToneQuest community. The global leaderboard spotlights
          the top writers, while the &ldquo;Around You&rdquo; view shows five writers ahead and four
          writers behind your current rank.
        </p>
      </header>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-semibold">Top 10 Global Writers</h2>
            <p className="text-sm text-muted-foreground">
              Highest average similarity scores across the entire platform.
            </p>
          </div>
          <Button variant="outline" onClick={() => refetchGlobal()}>
            Refresh
          </Button>
        </div>
        <LeaderboardTable
          entries={globalLeaderboard ?? []}
          isLoading={isGlobalLoading}
          isError={isGlobalError}
          emptyMessage="No leaderboard data available yet."
        />
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-semibold">Writers Around You</h2>
            <p className="text-sm text-muted-foreground">
              See how close you are to the next milestone. We show up to 5 writers ranked above you
              and 4 writers below.
            </p>
          </div>
          <Button variant="outline" onClick={() => refetchRelative()}>
            Refresh
          </Button>
        </div>

        {isRelativeError ? (
          <div className="rounded-md border border-dashed border-red-400 bg-red-50 p-4 text-sm text-red-700">
            We couldn&apos;t find your current placement yet. Submit an answer to join the
            leaderboard!
          </div>
        ) : (
          <div className="space-y-2">
            {relativeLeaderboard?.rank && (
              <p className="text-sm text-muted-foreground">
                You are currently ranked <span className="font-semibold">#{relativeLeaderboard.rank}</span>.
              </p>
            )}
            <LeaderboardTable
              entries={relativeLeaderboard?.entries ?? []}
              isLoading={isRelativeLoading}
              emptyMessage="Submit your first answer to appear on the leaderboard."
            />
          </div>
        )}
      </section>
    </div>
  );
};

