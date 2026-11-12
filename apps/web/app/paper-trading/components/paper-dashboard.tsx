"use client";

import { usePaperDashboard } from "@/lib/api/paper-trading";
import { AccountSummary } from "./account-summary";
import { PositionsTable } from './positions-table';
import { OrdersTable } from './orders-table';
import { TradesTable } from './trades-table';
import { PerformanceOverview } from './performance-overview';
import { OrderForm } from './order-form';

export function PaperDashboard() {
  const {
  data,
  isLoading,
  isFetching,
  isError,
  error,
  dataUpdatedAt,
  refetch,
} = usePaperDashboard();

  if (isLoading) {
    return <p>Loading paper trading dashboard...</p>;
  }

  if (isError) {
    return (
      <p className="text-red-500">
        {error.message}
      </p>
    );
  }

  if (!data) {
    return null;
  }

  const sbinPosition = (data.positions ?? []).find(
    (position) => position.symbol === 'NSE:SBIN-EQ',
  );

  return (
    <main className="space-y-6 p-6">

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Paper Trading Dashboard</h1>

          <p className="mt-1 text-sm text-gray-500">
            Last updated:{' '}
            {dataUpdatedAt
              ? new Date(dataUpdatedAt).toLocaleTimeString('en-IN')
              : 'Not updated yet'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            {isFetching ? 'Refreshing...' : 'Up to date'}
          </span>

          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="rounded-md border px-4 py-2 text-sm disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
      </div>

      <AccountSummary account={data.account} />

      <PositionsTable positions={data.positions ?? []} />

     <div className="grid grid-cols-1 gap-6">
        <OrdersTable orders={data.recent_orders ?? []} />
        <TradesTable trades={data.recent_trades ?? []} />
     </div>

     <PerformanceOverview
        performance={data.performance}
        equityCurve={data.equity_curve ?? []}
        pnlHistory={data.pnl_history ?? []}
      />

      <OrderForm
        availableBalance={data.account?.available_balance ?? 0}
        currentPrice={data.market?.current_price ?? 0}
        positionQuantity={sbinPosition?.quantity ?? 0}
      />
    </main>
  );
}