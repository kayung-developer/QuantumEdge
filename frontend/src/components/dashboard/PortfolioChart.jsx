import React, { useEffect, useRef, useCallback } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import ChartSpinner from '../common/ChartSpinner';

const PortfolioChart = ({ data }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const areaSeriesRef = useRef(null);

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
      grid: {
        vertLines: { visible: false },
        horzLines: { color: '#30363D' },
      },
      rightPriceScale: {
        borderColor: 'transparent',
      },
      timeScale: {
        borderColor: 'transparent',
        timeVisible: true,
        secondsVisible: false,
      },
       crosshair: {
        mode: 1,
      },
       handleScroll: {
        mouseWheel: false,
        pressedMouseMove: false,
      },
      handleScale: {
        mouseWheel: false,
        pinch: false,
      },
    });

    areaSeriesRef.current = chartRef.current.addAreaSeries({
      topColor: 'rgba(59, 130, 246, 0.4)',
      bottomColor: 'rgba(59, 130, 246, 0)',
      lineColor: '#3B82F6',
      lineWidth: 2,
    });

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
    if (areaSeriesRef.current && data && data.length > 0) {
       const formattedData = data.map(item => ({
        time: new Date(item.time).getTime() / 1000,
        value: item.value,
      }));
      areaSeriesRef.current.setData(formattedData);
      chartRef.current.timeScale().fitContent();
    }
  }, [data]);

  const isLoading = !data || data.length === 0;

  return (
    <div className="w-full h-full relative" ref={chartContainerRef}>
      {isLoading && <ChartSpinner text="Loading portfolio data..." />}
    </div>
  );
};

export default PortfolioChart;