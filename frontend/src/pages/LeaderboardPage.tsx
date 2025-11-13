import { Button } from "@/components/ui/button";
import { LeaderboardTable } from "@/components/leaderboard/LeaderboardTable";
import { useGlobalLeaderboard, useRelativeLeaderboard } from "@/hooks/queries/useLeaderboardQueries";

export const LeaderboardPage = () => {
  const {
    data: globalLeaderboard,
    isLoading: isGlobalLoading,
    isError: isGlobalError,
    isFetching: isGlobalFetching,
    refetch: refetchGlobal,
  } = useGlobalLeaderboard();

  const {
    data: relativeLeaderboard,
    isLoading: isRelativeLoading,
    isError: isRelativeError,
    isFetching: isRelativeFetching,
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
          <Button variant="outline" onClick={() => refetchGlobal()} disabled={isGlobalFetching}>
            {isGlobalFetching ? (
              <>
                <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Refreshing...
              </>
            ) : (
              'Refresh'
            )}
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
          <Button variant="outline" onClick={() => refetchRelative()} disabled={isRelativeFetching}>
            {isRelativeFetching ? (
              <>
                <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Refreshing...
              </>
            ) : (
              'Refresh'
            )}
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

