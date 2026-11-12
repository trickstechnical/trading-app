'use client';

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from 'recharts';

import type {
  EquityPoint,
  PnlPoint,
  PerformanceStats,
} from '@/types/paper-trading';

interface PerformanceOverviewProps {
  performance?: PerformanceStats;
  equityCurve?: EquityPoint[];
  pnlHistory?: PnlPoint[];
}

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
  });
}

export function PerformanceOverview({
  performance,
  equityCurve = [],
  pnlHistory = [],
}: PerformanceOverviewProps) {
  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Trading Performance</h2>
        <p className="text-sm text-gray-500">
          Review your realized trading results.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total Trades" value={performance?.total_trades ?? 0} />
        <StatCard
          label="Win Rate"
          value={`${(performance?.win_rate ?? 0).toFixed(2)}%`}
        />
        <StatCard
          label="Profit Factor"
          value={
            performance?.profit_factor !== null &&
            performance?.profit_factor !== undefined &&
            Number.isFinite(performance.profit_factor)
              ? performance.profit_factor.toFixed(2)
              : '—'
          }
        />
        <StatCard
          label="Max Drawdown"
          value={currencyFormatter.format(performance?.max_drawdown ?? 0)}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <h3 className="font-semibold">Realized Equity Curve</h3>
          <p className="mb-4 text-sm text-gray-500">
            Initial capital plus cumulative realized P&L
          </p>

          {(equityCurve?.length ?? 0) < 2 ? (
            <EmptyChartMessage />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={equityCurve}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatDate}
                  minTickGap={30}
                />
                <YAxis
                  tickFormatter={(value: number) =>
                    `₹${Number(value).toLocaleString('en-IN')}`
                  }
                  width={85}
                />
                <Tooltip
                  labelFormatter={(value) => formatDate(String(value))}
                  formatter={(value) => [
                    currencyFormatter.format(Number(value)),
                    'Equity',
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="equity"
                  name="Equity"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="rounded-lg border bg-white p-6">
          <h3 className="font-semibold">Realized P&L by Trade</h3>
          <p className="mb-4 text-sm text-gray-500">
            Net profit or loss for each completed trade
          </p>

          {(pnlHistory?.length ?? 0) === 0 ? (
            <EmptyChartMessage />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={pnlHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatDate}
                  minTickGap={30}
                />
                <YAxis
                  tickFormatter={(value: number) =>
                    `₹${Number(value).toLocaleString('en-IN')}`
                  }
                  width={85}
                />
                <Tooltip
                  labelFormatter={(value) => formatDate(String(value))}
                  formatter={(value) => [
                    currencyFormatter.format(Number(value)),
                    'Net P&L',
                  ]}
                />
                <Bar
                  dataKey="realized_pnl"
                  name="Net P&L"
                  fill="#2563eb"
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </section>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
    </div>
  );
}

function EmptyChartMessage() {
  return (
    <div className="flex h-[280px] items-center justify-center text-sm text-gray-500">
      Complete a paper trade to see performance data.
    </div>
  );
}