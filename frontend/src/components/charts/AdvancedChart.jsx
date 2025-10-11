import React, { useEffect, useRef, useCallback } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import useMarketDataStore from '../../store/marketDataStore';
import ChartSpinner from '../common/ChartSpinner';

const AdvancedChart = () => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);

  const { kline } = useMarketDataStore();
  const { data: chartData, loading: isLoading } = kline;

  const handleResize = useCallback(() => {
    if (chartRef.current && chartContainerRef.current) {
      chartRef.current.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
      });
    }
  }, []);

  useEffect(() => {
    if (!chartContainerRef.current || chartRef.current) return;

    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: { background: { type: ColorType.Solid, color: '#161B22' }, textColor: '#8B949E' },
      grid: { vertLines: { color: '#30363D' }, horzLines: { color: '#30363D' } },
      crosshair: { mode: 1 },
      rightPriceScale: { borderColor: '#30363D' },
      timeScale: { borderColor: '#30363D', timeVisible: true, secondsVisible: false },
    });

    candlestickSeriesRef.current = chartRef.current.addCandlestickSeries({
      upColor: '#22C55E', downColor: '#EF4444', borderDownColor: '#EF4444',
      borderUpColor: '#22C55E', wickDownColor: '#EF4444', wickUpColor: '#22C55E',
    });

    volumeSeriesRef.current = chartRef.current.addHistogramSeries({
      color: '#30363D', priceFormat: { type: 'volume' }, priceScaleId: '',
    });
    chartRef.current.priceScale('').applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [handleResize]);

  useEffect(() => {
    if (candlestickSeriesRef.current && volumeSeriesRef.current && chartData?.length > 0) {
      candlestickSeriesRef.current.setData(chartData);
      const volumeData = chartData.map(d => ({
        time: d.time, value: d.volume,
        color: d.close > d.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)',
      }));
      volumeSeriesRef.current.setData(volumeData);
      chartRef.current.timeScale().fitContent();
    }
  }, [chartData]);

  useEffect(() => {
    if (candlestickSeriesRef.current && volumeSeriesRef.current && chartData?.length > 0) {
      const lastCandle = chartData[chartData.length - 1];
      candlestickSeriesRef.current.update(lastCandle);
      const lastVolume = {
        time: lastCandle.time, value: lastCandle.volume,
        color: lastCandle.close > lastCandle.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)',
      };
      volumeSeriesRef.current.update(lastVolume);
    }
  }, [chartData ? chartData[chartData.length - 1] : null]);

  return (
    <div className="w-full h-full relative" ref={chartContainerRef}>
      {isLoading && <ChartSpinner />}
    </div>
  );
};

export default AdvancedChart;