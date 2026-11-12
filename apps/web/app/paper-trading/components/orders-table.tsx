'use client';

import type { PaperOrder } from '@/types/paper-trading';

interface OrdersTableProps {
  orders?: PaperOrder[];
}

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
});

function formatDate(value: string) {
  return new Date(value).toLocaleString('en-IN');
}

export function OrdersTable({ orders = [] }: OrdersTableProps) {
  return (
    <div className="rounded-lg border bg-white p-6">
      <h2 className="text-lg font-semibold">Recent Orders</h2>

      {(orders?.length ?? 0) === 0 ? (
        <p className="mt-4 text-sm text-gray-500">No orders yet.</p>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[750px] text-left text-sm">
            <thead>
              <tr className="border-b text-gray-500">
                <th className="px-3 py-3 font-medium">Date</th>
                <th className="px-3 py-3 font-medium">Symbol</th>
                <th className="px-3 py-3 font-medium">Side</th>
                <th className="px-3 py-3 text-right font-medium">Quantity</th>
                <th className="px-3 py-3 text-right font-medium">Price</th>
                <th className="px-3 py-3 text-right font-medium">Total</th>
                <th className="px-3 py-3 font-medium">Status</th>
              </tr>
            </thead>

            <tbody>
              {orders.map((order) => (
                <tr key={order.id} className="border-b last:border-0">
                  <td className="px-3 py-4 whitespace-nowrap">
                    {formatDate(order.created_at)}
                  </td>
                  <td className="px-3 py-4">{order.symbol}</td>
                  <td
                    className={`px-3 py-4 font-medium ${
                      order.side === 'BUY' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {order.side}
                  </td>
                  <td className="px-3 py-4 text-right">{order.quantity}</td>
                  <td className="px-3 py-4 text-right">
                    {currencyFormatter.format(order.price)}
                  </td>
                  <td className="px-3 py-4 text-right">
                    {currencyFormatter.format(order.total_value ?? (order.price * order.quantity))}
                  </td>
                  <td className="px-3 py-4">{order.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}