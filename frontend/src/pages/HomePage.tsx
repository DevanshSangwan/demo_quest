import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";
import { useScoreHistory, useRankHistory } from "@/hooks/queries/useUserQueries";
import { ScoreHistoryChart } from "@/components/charts/ScoreHistoryChart";
import { RankHistoryChart } from "@/components/charts/RankHistoryChart";

const pages = [
  {
    title: "Start Answering",
    description:
      "Practice with curated prompts, submit thoughtful responses, and watch your writing skills improve.",
    action: "Go to Answering",
    href: "/answer",
  },
  {
    title: "View Leaderboards",
    description:
      "See the global top writers and how you rank compared to peers with similar scores.",
    action: "Open Leaderboards",
    href: "/leaderboard",
  },
  {
    title: "Your Profile",
    description:
      "Check your submission stats, best score, and progress over time in one quick glance.",
    action: "View Profile",
    href: "/user",
  },
];

export const HomePage = () => {
  const { user } = useAuthStore();
  const { data: scoreHistory, isLoading: isScoreLoading } = useScoreHistory();
  const { data: rankHistory, isLoading: isRankHistoryLoading } = useRankHistory();

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="grid grid-cols-1 items-center gap-8 py-12 md:grid-cols-2 md:py-16">
        {/* Left Column - Text & CTA */}
        <div className="space-y-6 pr-8">
          <h1 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl lg:text-6xl">
            Master Your Professional Tone.
          </h1>
          <p className="text-lg text-muted-foreground md:text-xl">
            Get instant, AI-driven feedback on your writing. Improve your clarity and effectiveness
            for the modern workplace.
          </p>
          <div>
            <Button asChild size="lg" className="bg-blue-500 text-base text-white hover:bg-blue-600">
              {user ? (
                <Link to="/answer">Start Learning</Link>
              ) : (
                <Link to="/auth">Start Your Evaluation</Link>
              )}
            </Button>
          </div>
        </div>

        {/* Right Column - Image */}
        <div className="flex items-center justify-center">
          <img
            src="/hero-quest.png"
            alt="Person learning on tablet"
            className="h-auto w-full max-w-lg rounded-lg object-contain"
          />
        </div>
      </section>

      {user && !isScoreLoading && !isRankHistoryLoading && 
       ((scoreHistory && scoreHistory.length > 0) || (rankHistory && rankHistory.length > 0)) && (
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold">Track Your Progress</h2>
          <div className="grid gap-6 md:grid-cols-2">
            <ScoreHistoryChart data={scoreHistory || []} />
            <RankHistoryChart data={rankHistory || []} />
          </div>
        </section>
      )}

      <section className="grid gap-6 md:grid-cols-3">
        {pages.map((page) => (
          <article
            key={page.title}
            className="flex h-full flex-col rounded-2xl border border-border bg-background p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
          >
            <h2 className="text-xl font-semibold">{page.title}</h2>
            <p className="mt-3 flex-1 text-sm text-muted-foreground">{page.description}</p>
            <Button asChild className="mt-6">
              <Link to={page.href}>{page.action}</Link>
            </Button>
          </article>
        ))}
      </section>

      {user && (
        <section className="rounded-2xl border border-dashed border-border bg-background p-6">
          <h3 className="text-lg font-semibold">Not sure where to begin?</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Start with a fresh prompt on the answering page, then review how you stack up on the
            leaderboard and keep your profile up-to-date.
          </p>
        </section>
      )}
    </div>
  );
};