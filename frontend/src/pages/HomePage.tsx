import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

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
  return (
    <div className="space-y-12">
      <section className="rounded-3xl bg-gradient-to-br from-primary/90 via-primary to-primary/80 p-10 text-white shadow-xl">
        <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
          Welcome back to ToneQuest
        </h1>
        <p className="mt-4 max-w-3xl text-lg text-white/90">
          Hone your professional writing by answering scenario-based prompts, learn from detailed
          feedback, and climb the leaderboard as you improve. Use the shortcuts below to jump
          straight into today&apos;s goals.
        </p>
      </section>

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

      <section className="rounded-2xl border border-dashed border-border bg-background p-6">
        <h3 className="text-lg font-semibold">Not sure where to begin?</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Start with a fresh prompt on the answering page, then review how you stack up on the
          leaderboard and keep your profile up-to-date.
        </p>
      </section>
    </div>
  );
};