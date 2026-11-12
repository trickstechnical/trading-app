'use client';

import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface OrderFormProps {
  availableBalance: number;
  currentPrice: number;
  positionQuantity: number;
}

type OrderSide = 'BUY' | 'SELL';

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
});

export function OrderForm({
  availableBalance,
  currentPrice,
  positionQuantity,
}: OrderFormProps) {
  const queryClient = useQueryClient();

  const [side, setSide] = useState<OrderSide>('BUY');
  const [quantity, setQuantity] = useState('1');
  const [isConfirming, setIsConfirming] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const parsedQuantity = Number(quantity);
  const isValidQuantity =
    Number.isInteger(parsedQuantity) && parsedQuantity > 0;

  const estimatedValue = isValidQuantity
    ? parsedQuantity * currentPrice
    : 0;

  const hasSufficientBalance = estimatedValue <= availableBalance;
  const hasSufficientPosition = parsedQuantity <= positionQuantity;

  const validationMessage = !isValidQuantity
    ? 'Enter a valid whole-number quantity greater than zero.'
    : side === 'BUY' && !hasSufficientBalance
      ? 'Insufficient available balance for this order.'
      : side === 'SELL' && !hasSufficientPosition
        ? `You only have ${positionQuantity} shares available to sell.`
        : '';

  async function submitOrder() {
    if (validationMessage || isSubmitting) return;

    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/paper-trading/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: 'NSE:SBIN-EQ',
          side,
          quantity: parsedQuantity,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || result.message || 'Order failed.');
      }

      setSuccess(`${side} paper order placed successfully.`);
      setQuantity('1');
      setIsConfirming(false);

      await queryClient.invalidateQueries({
        queryKey: ['paper-trading', 'dashboard'],
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to place paper order.',
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="rounded-lg border bg-white p-6">
      <h2 className="text-lg font-semibold">Place Paper Order</h2>
      <p className="mt-1 text-sm text-gray-500">
        Orders are simulated using your latest completed market candle.
      </p>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => {
            setSide('BUY');
            setIsConfirming(false);
            setError('');
          }}
          className={`rounded-md border px-4 py-2 font-medium ${
            side === 'BUY'
              ? 'border-green-600 bg-green-50 text-green-700'
              : 'border-gray-200'
          }`}
        >
          BUY
        </button>

        <button
          type="button"
          onClick={() => {
            setSide('SELL');
            setIsConfirming(false);
            setError('');
          }}
          className={`rounded-md border px-4 py-2 font-medium ${
            side === 'SELL'
              ? 'border-red-600 bg-red-50 text-red-700'
              : 'border-gray-200'
          }`}
        >
          SELL
        </button>
      </div>

      <div className="mt-5">
        <label htmlFor="paper-quantity" className="text-sm font-medium">
          Quantity
        </label>
        <input
          id="paper-quantity"
          type="number"
          min="1"
          step="1"
          value={quantity}
          onChange={(event) => {
            setQuantity(event.target.value);
            setIsConfirming(false);
            setError('');
          }}
          className="mt-2 w-full rounded-md border px-3 py-2 outline-none focus:border-blue-500"
        />
      </div>

      <div className="mt-5 space-y-2 rounded-md bg-gray-50 p-4 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Instrument</span>
          <span className="font-medium">NSE:SBIN-EQ</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Estimated price</span>
          <span>{currencyFormatter.format(currentPrice)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Estimated order value</span>
          <span className="font-semibold">
            {currencyFormatter.format(estimatedValue)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Available balance</span>
          <span>{currencyFormatter.format(availableBalance)}</span>
        </div>
        {side === 'SELL' && (
          <div className="flex justify-between">
            <span className="text-gray-500">Available quantity</span>
            <span>{positionQuantity}</span>
          </div>
        )}
      </div>

      {validationMessage && (
        <p className="mt-3 text-sm text-red-600">{validationMessage}</p>
      )}

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      {success && <p className="mt-3 text-sm text-green-600">{success}</p>}

      {isConfirming ? (
        <div className="mt-5 rounded-md border p-4">
          <p className="text-sm">
            Confirm paper {side} of {parsedQuantity} SBIN shares for an
            estimated value of {currencyFormatter.format(estimatedValue)}?
          </p>
          <div className="mt-4 flex gap-3">
            <button
              type="button"
              onClick={() => setIsConfirming(false)}
              disabled={isSubmitting}
              className="flex-1 rounded-md border px-4 py-2 text-sm"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={submitOrder}
              disabled={isSubmitting}
              className="flex-1 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {isSubmitting ? 'Submitting...' : 'Confirm Order'}
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setIsConfirming(true)}
          disabled={Boolean(validationMessage) || currentPrice <= 0}
          className="mt-5 w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Review {side} Order
        </button>
      )}
    </div>
  );
}