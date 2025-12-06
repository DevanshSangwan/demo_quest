import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { ScoreHistoryEntry } from '@/api/services/userService';

interface ScoreHistoryChartProps {
  data: ScoreHistoryEntry[];
}

export const ScoreHistoryChart = ({ data }: ScoreHistoryChartProps) => {
  const chartData = data.map((entry, index) => ({
    attemptNumber: index + 1,
    score: entry.score,
    questionId: entry.question_id,
  }));

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-4 text-lg font-semibold">Score Progress</h3>
      {chartData.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">
          Submit answers to see your score progress
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="attemptNumber" 
              label={{ value: 'Attempt Number', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              domain={[0, 100]}
              label={{ value: 'Score', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-md">
                      <p className="text-sm font-semibold">Attempt #{data.attemptNumber}</p>
                      <p className="text-sm">Question ID: {data.questionId}</p>
                      <p className="text-sm">Score: {data.score.toFixed(1)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};
