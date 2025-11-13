import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "@/firebaseConfig";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/leaderboard", label: "Leaderboard" },
  { to: "/answer", label: "Answering" },
  { to: "/user", label: "User Info" },
];

export const AppShell = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate("/auth", { replace: true });
    } catch (error) {
      console.error("Failed to log out:", error);
    }
  };

  return (
    <div className="min-h-screen bg-muted/20">
      <header className="bg-white shadow">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <Link to="/" className="text-xl font-semibold">
            ToneQuest
          </Link>
          <nav className="hidden gap-6 text-sm font-medium sm:flex">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  isActive
                    ? "text-primary underline underline-offset-4"
                    : "text-muted-foreground hover:text-foreground"
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-4">
            {user && (
              <span className="hidden text-sm text-muted-foreground sm:inline">
                {user.displayName ?? user.email ?? "Authenticated"}
              </span>
            )}
            <Button variant="outline" onClick={handleLogout}>
              Log out
            </Button>
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
};

