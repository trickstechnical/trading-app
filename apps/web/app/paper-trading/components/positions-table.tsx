'use client';

import type { PaperPosition } from '@/types/paper-trading';

interface PositionsTableProps {
  positions?: PaperPosition[];
}

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
});

function formatPrice(value: number | null) {
  if (value === null) return '—';
  return currencyFormatter.format(value);
}

export function PositionsTable({ positions = [] }: PositionsTableProps) {
  if (!positions || (positions?.length ?? 0) === 0) {
    return (
      <div className="rounded-lg border bg-white p-6">
        <h2 className="text-lg font-semibold">Open Positions</h2>
        <p className="mt-4 text-sm text-gray-500">
          You don&apos;t have any open positions.
        </p>
      </div>
    );
  }

  const count = positions?.length ?? 0;

  return (
    <div className="rounded-lg border bg-white p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold">Open Positions</h2>
        <p className="text-sm text-gray-500">
          {count} open {count === 1 ? 'position' : 'positions'}
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="px-3 py-3 font-medium">Symbol</th>
              <th className="px-3 py-3 text-right font-medium">Quantity</th>
              <th className="px-3 py-3 text-right font-medium">Avg. Price</th>
              <th className="px-3 py-3 text-right font-medium">LTP</th>
              <th className="px-3 py-3 text-right font-medium">Stop-loss</th>
              <th className="px-3 py-3 text-right font-medium">Target</th>
              <th className="px-3 py-3 text-right font-medium">Unrealized P&L</th>
            </tr>
          </thead>

          <tbody>
            {positions.map((position, index) => {
              const isProfit = position.unrealized_pnl >= 0;

              return (
                <tr key={index} className="border-b last:border-0">
                  <td className="px-3 py-4 font-medium">{position.symbol}</td>
                  <td className="px-3 py-4 text-right">{position.quantity}</td>
                  <td className="px-3 py-4 text-right">
                    {formatPrice(position.average_price)}
                  </td>
                  <td className="px-3 py-4 text-right">
                    {formatPrice(position.current_price)}
                  </td>
                  <td className="px-3 py-4 text-right">
                    {formatPrice(position.stop_loss)}
                  </td>
                  <td className="px-3 py-4 text-right">
                    {formatPrice(position.target_price)}
                  </td>
                  <td
                    className={`px-3 py-4 text-right font-medium ${
                      isProfit ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {isProfit ? '+' : ''}
                    {formatPrice(position.unrealized_pnl)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}