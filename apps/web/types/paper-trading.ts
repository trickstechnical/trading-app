export interface PaperPosition {
  id: number;
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  stop_loss: number | null;
  target_price: number | null;
  unrealized_pnl: number;
}

export interface PaperOrder {
  id: number;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  total_value: number;
  charges: number;
  status: string;
  order_type: string;
  created_at: string;
}

export interface PaperTrade {
  id: number;
  symbol: string;
  quantity: number;
  entry_price: number;
  exit_price: number;
  gross_pnl: number;
  net_pnl: number;
  realized_pnl: number;
  exit_reason: string;
  created_at: string;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface PnlPoint {
  timestamp: string;
  realized_pnl: number;
}

export interface PerformanceStats {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  gross_profit: number;
  gross_loss: number;
  net_pnl: number;
  profit_factor: number | null;
  average_win: number;
  average_loss: number;
  max_drawdown: number;
}