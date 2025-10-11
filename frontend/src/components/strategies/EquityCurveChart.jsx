import React, { useEffect, useRef, useCallback } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import ChartSpinner from '../common/ChartSpinner';

const EquityCurveChart = ({ data, initialCapital }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const areaSeriesRef = useRef(null);
  const baselineSeriesRef = useRef(null);

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
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#8B949E',
      },
      grid: { vertLines: { visible: false }, horzLines: { color: '#30363D' } },
      rightPriceScale: { borderColor: 'transparent' },
      timeScale: { borderColor: 'transparent', timeVisible: true },
    });

    areaSeriesRef.current = chartRef.current.addAreaSeries({
      topColor: 'rgba(59, 130, 246, 0.5)',
      bottomColor: 'rgba(59, 130, 246, 0)',
      lineColor: '#3B82F6',
      lineWidth: 2,
    });

    // Add a baseline for the initial capital
    baselineSeriesRef.current = chartRef.current.addLineSeries({
        color: '#8B949E',
        lineWidth: 1,
        lineStyle: 2, // Dotted
        priceLineVisible: false,
        lastValueVisible: false,
    });

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      if (chartRef.current) chartRef.current.remove();
      chartRef.current = null;
    };
  }, [handleResize]);

  useEffect(() => {
    if (areaSeriesRef.current && baselineSeriesRef.current && data && Object.keys(data).length > 0) {
      const formattedData = Object.entries(data).map(([time, value]) => ({
        time: new Date(time).getTime() / 1000,
        value: value,
      }));

      areaSeriesRef.current.setData(formattedData);

      // Set the baseline data
      if (formattedData.length > 0) {
        baselineSeriesRef.current.setData([
            { time: formattedData[0].time, value: initialCapital },
            { time: formattedData[formattedData.length - 1].time, value: initialCapital }
        ]);
      }

      chartRef.current.timeScale().fitContent();
    }
  }, [data, initialCapital]);

  const isLoading = !data || Object.keys(data).length === 0;

  return (
    <div className="w-full h-full relative" ref={chartContainerRef}>
      {isLoading && <ChartSpinner text="Generating equity curve..." />}
    </div>
  );
};

export default EquityCurveChart;