import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { RankHistoryEntry } from '@/api/services/userService';

interface RankHistoryChartProps {
  data: RankHistoryEntry[];
}

export const RankHistoryChart = ({ data }: RankHistoryChartProps) => {
  const chartData = data.map((entry) => ({
    date: entry.date,
    rank: entry.rank,
    displayDate: new Date(entry.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-4 text-lg font-semibold">Rank History</h3>
      {chartData.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">
          Rank history will be available starting tomorrow (snapshots taken daily at 4 AM)
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="displayDate" 
              label={{ value: 'Date', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              reversed={true}
              allowDecimals={false}
              domain={['dataMin - 1', 'dataMax + 1']}
              label={{ value: 'Rank', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-md">
                      <p className="text-sm font-semibold">{data.displayDate}</p>
                      <p className="text-sm">Rank: #{data.rank}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Line type="monotone" dataKey="rank" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};
