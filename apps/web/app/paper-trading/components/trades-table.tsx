'use client';

import type { PaperTrade } from '@/types/paper-trading';

interface TradesTableProps {
  trades?: PaperTrade[];
}

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
});

function formatDate(value: string) {
  return new Date(value).toLocaleString('en-IN');
}

export function TradesTable({ trades = [] }: TradesTableProps) {
  return (
    <div className="rounded-lg border bg-white p-6">
      <h2 className="text-lg font-semibold">Recent Trades</h2>

      {(trades?.length ?? 0) === 0 ? (
        <p className="mt-4 text-sm text-gray-500">No completed trades yet.</p>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[750px] text-left text-sm">
            <thead>
              <tr className="border-b text-gray-500">
                <th className="px-3 py-3 font-medium">Exit Date</th>
                <th className="px-3 py-3 font-medium">Symbol</th>
                <th className="px-3 py-3 text-right font-medium">Quantity</th>
                <th className="px-3 py-3 text-right font-medium">Entry</th>
                <th className="px-3 py-3 text-right font-medium">Exit</th>
                <th className="px-3 py-3 font-medium">Exit Reason</th>
                <th className="px-3 py-3 text-right font-medium">Net P&L</th>
              </tr>
            </thead>

            <tbody>
              {trades.map((trade) => {
                const pnl = trade.net_pnl ?? trade.realized_pnl ?? 0;

                return (
                  <tr key={trade.id} className="border-b last:border-0">
                    <td className="px-3 py-4 whitespace-nowrap">
                      {formatDate(trade.created_at)}
                    </td>
                    <td className="px-3 py-4">{trade.symbol}</td>
                    <td className="px-3 py-4 text-right">{trade.quantity}</td>
                    <td className="px-3 py-4 text-right">
                      {currencyFormatter.format(trade.entry_price)}
                    </td>
                    <td className="px-3 py-4 text-right">
                      {currencyFormatter.format(trade.exit_price)}
                    </td>
                    <td className="px-3 py-4">{trade.exit_reason}</td>
                    <td
                      className={`px-3 py-4 text-right font-medium ${
                        pnl >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {pnl >= 0 ? '+' : ''}
                      {currencyFormatter.format(pnl)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}