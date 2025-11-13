import { LeaderboardTable } from '@/components/leaderboard/LeaderboardTable';
import { NewEntryForm } from '@/components/leaderboard/NewEntryForm';

export const DashboardPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Add New Entry</h2>
          <NewEntryForm />
        </div>
        
        <div>
          <h2 className="text-2xl font-semibold mb-4">Leaderboard</h2>
          <LeaderboardTable />
        </div>
      </div>
    </div>
  );
};