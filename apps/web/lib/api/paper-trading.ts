import { useQuery } from "@tanstack/react-query";
import { PaperPosition, PaperTrade, PaperOrder, PerformanceStats, EquityPoint, PnlPoint } from "@/types/paper-trading";

export interface PaperDashboard {
  account: {
    initial_balance: number;
    available_balance: number;
    market_value: number;
    equity: number;
    realized_pnl: number;
    unrealized_pnl: number;
    total_pnl: number;
    return_percentage: number;
  };
  positions: PaperPosition[];
  recent_orders: PaperOrder[];
  recent_trades: PaperTrade[];
  performance: PerformanceStats;
  equity_curve: EquityPoint[];
  pnl_history: PnlPoint[];
  market?: {
    symbol: string;
    current_price: number;
  };
}

async function fetchPaperDashboard(): Promise<PaperDashboard> {
  const response = await fetch('/api/paper-trading/dashboard', {
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Failed to fetch paper-trading dashboard.');
  }

  return response.json();
}

export function usePaperDashboard() {
  return useQuery({
    queryKey: ['paper-trading', 'dashboard'],
    queryFn: fetchPaperDashboard,
    staleTime: 5_000,
    refetchInterval: 10_000,
    refetchIntervalInBackground: false,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  });
}