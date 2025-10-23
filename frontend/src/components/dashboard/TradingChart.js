import React, { memo, useState } from 'react';
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import api from 'services/api';
import { useTheme } from 'contexts/ThemeContext';
import toast from 'react-hot-toast';
import useSWR from 'swr';

// ==============================================================================
// SUB-COMPONENT: CandlestickShape (DEFINITIVE, MATHEMATICALLY CORRECT VERSION)
// ==============================================================================
const CandlestickShape = (props) => {
  // Guard against the initial render pass where yAxis might be undefined
  if (!props.yAxis || typeof props.yAxis.scale !== 'function') {
    return null;
  }

  const { x, width, payload, yAxis } = props;
  const { open, close, high, low } = payload;

  const isRising = close >= open;
  const color = isRising ? '#22C55E' : '#EF4444';
  const wickX = x + width / 2;

  // --- THE DEFINITIVE FIX IS HERE ---
  // Convert all data points (prices) to pixel coordinates on the Y-axis
  const yHigh = yAxis.scale(high);
  const yLow = yAxis.scale(low);
  const yOpen = yAxis.scale(open);
  const yClose = yAxis.scale(close);

  // The body of the candle is a rectangle between the open and close coordinates
  const bodyY = Math.min(yOpen, yClose);
  const bodyHeight = Math.max(1, Math.abs(yOpen - yClose)); // Ensure a 1px body for doji candles
  // --- END OF FIX ---

  return (
    <g>
      {/* Wick: A single line from the high to the low pixel coordinate */}
      <line x1={wickX} y1={yHigh} x2={wickX} y2={yLow} stroke={color} strokeWidth="1.5" />
      {/* Body: The rectangle drawn with the correct coordinates and height */}
      <rect x={x} y={bodyY} width={width} height={bodyHeight} fill={color} />
    </g>
  );
};

// ==============================================================================
// SUB-COMPONENT: CustomTooltip (No changes needed, but included for completeness)
// ==============================================================================
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    if (!data) return null;
    return (
      <div className="p-3 bg-white/90 dark:bg-dark-card/90 backdrop-blur-sm border border-gray-300 dark:border-dark-border rounded-lg shadow-xl text-xs">
        <p className="font-bold">{new Date(data.time * 1000).toLocaleString()}</p>
        <div className="grid grid-cols-2 gap-x-4 mt-2">
            <span>Open:</span><span className="font-mono text-right">{data.open?.toFixed(5)}</span>
            <span>High:</span><span className="font-mono text-right">{data.high?.toFixed(5)}</span>
            <span>Low:</span><span className="font-mono text-right">{data.low?.toFixed(5)}</span>
            <span>Close:</span><span className="font-mono text-right">{data.close?.toFixed(5)}</span>
            <span>Volume:</span><span className="font-mono text-right">{data.real_volume?.toLocaleString()}</span>
        </div>
      </div>
    );
  }
  return null;
};


const TimeframeSelector = ({ selected, onSelect }) => {
    const timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1'];

    const baseClasses = "px-3 py-1 text-sm font-semibold rounded-md transition-colors duration-200";
    const activeClasses = "bg-primary text-white shadow-md";
    const inactiveClasses = "text-gray-500 dark:text-dark-text-secondary hover:bg-gray-200 dark:hover:bg-dark-border/30";

    return (
        <div className="flex items-center space-x-2 p-1 bg-gray-100 dark:bg-dark-bg rounded-lg">
            {timeframes.map(tf => (
                <button
                    key={tf}
                    onClick={() => onSelect(tf)}
                    className={`${baseClasses} ${selected === tf ? activeClasses : inactiveClasses}`}
                >
                    {tf}
                </button>
            ))}
        </div>
    );
};
// ==============================================================================
// MAIN COMPONENT: TradingChart (No changes needed, but included for completeness)
// ==============================================================================
const TradingChart = ({ symbol = 'EURUSD' }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

   const [timeframe, setTimeframe] = useState('H1'); // Default to H1
  const fetcher = (url) => api.get(url).then(res => res.data);
  const { data: chartData, error, isLoading } = useSWR(`/mt5/history/${symbol}?timeframe=${timeframe}&count=100`, fetcher, {
    refreshInterval: 60000,
  });

  if (error) {
    toast.error(`Failed to load ${timeframe} chart data.`, { id: `chart-error-${timeframe}` });
    return <div className="w-full h-[400px] flex items-center justify-center text-danger bg-danger/5 rounded-lg p-4">Could not load chart data.</div>;
  }

  if (isLoading || !chartData) {
    return <div className="w-full h-[400px] bg-gray-200 dark:bg-dark-border/20 rounded-lg animate-pulse" />;
  }

  const data = chartData.map(d => ({
    time: new Date(d.time).getTime() / 1000,
    open: d.open, high: d.high, low: d.low, close: d.close,
    real_volume: d.real_volume,
    body: [Math.min(d.open, d.close), Math.max(d.open, d.close)],
  }));

  const yDomainValues = data.flatMap(d => [d.low, d.high]);
  const yMin = Math.min(...yDomainValues);
  const yMax = Math.max(...yDomainValues);
  const yPadding = (yMax - yMin) * 0.1;

  // Function to format the date on the X-axis based on the timeframe
  const formatXAxis = (time) => {
    const date = new Date(time * 1000);
    if (['D1', 'W1', 'MN1'].includes(timeframe)) {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    // The component now returns a fragment containing the selector and the chart
    <>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-light-text dark:text-dark-text">
          {symbol} <span className="text-base font-normal text-gray-500 dark:text-dark-text-secondary">({timeframe})</span>
        </h2>
        <TimeframeSelector selected={timeframe} onSelect={setTimeframe} />
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid stroke={isDark ? '#30363D' : '#E5E7EB'} strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            tickFormatter={formatXAxis}
            stroke={isDark ? '#8B949E' : '#6B7280'}
            tick={{ fontSize: 10 }}
          />
          <YAxis
            orientation="right"
            domain={[yMin - yPadding, yMax + yPadding]}
            tickFormatter={(value) => typeof value === 'number' ? value.toFixed(5) : ''}
            stroke={isDark ? '#8B949E' : '#6B7280'}
            tick={{ fontSize: 10 }}
            width={80}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="body" shape={<CandlestickShape />} />
        </ComposedChart>
      </ResponsiveContainer>
    </>
  );
};
export default memo(TradingChart);