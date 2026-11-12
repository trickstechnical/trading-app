"use client";

import type { PaperDashboard } from "@/lib/api/paper-trading";

interface AccountSummaryProps {
  account?: PaperDashboard["account"];
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}

function SummaryCard({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive?: boolean;
}) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <p className="text-sm text-gray-500">{label}</p>

      <p
        className={`mt-2 text-2xl font-semibold ${
          positive === undefined
            ? "text-gray-900"
            : positive
              ? "text-green-600"
              : "text-red-600"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

export function AccountSummary({ account }: AccountSummaryProps) {
  const isPositive = (account?.total_pnl ?? 0) >= 0;

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Account Overview</h2>

        <span
          className={
            isPositive
              ? "text-sm font-medium text-green-600"
              : "text-sm font-medium text-red-600"
          }
        >
          {isPositive ? "+" : ""}
          {account?.return_percentage ?? 0}% return
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <SummaryCard
          label="Initial Capital"
          value={formatCurrency(account?.initial_balance ?? 0)}
        />

        <SummaryCard
          label="Available Balance"
          value={formatCurrency(account?.available_balance ?? 0)}
        />

        <SummaryCard
          label="Invested Value"
          value={formatCurrency(account?.market_value ?? 0)}
        />

        <SummaryCard
          label="Portfolio Equity"
          value={formatCurrency(account?.equity ?? 0)}
        />

        <SummaryCard
          label="Realized P&L"
          value={formatCurrency(account?.realized_pnl ?? 0)}
          positive={(account?.realized_pnl ?? 0) >= 0}
        />

        <SummaryCard
          label="Unrealized P&L"
          value={formatCurrency(account?.unrealized_pnl ?? 0)}
          positive={(account?.unrealized_pnl ?? 0) >= 0}
        />
      </div>
    </section>
  );
}