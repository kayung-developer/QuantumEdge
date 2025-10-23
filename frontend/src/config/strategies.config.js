import { BeakerIcon, ChartBarIcon, ScaleIcon, ArrowsRightLeftIcon, CpuChipIcon, CurrencyDollarIcon, ArrowTrendingUpIcon, CloudIcon, SparklesIcon } from '@heroicons/react/24/outline';


const BASE_STRATEGIES = {
    EmaCrossAtr: { value: "EmaCrossAtr", label: "Adaptive EMA Crossover" },
    RsiBbMeanReversion: { value: "RsiBbMeanReversion", label: "RSI & Bollinger Reversion" },
    MacdAdxTrend: { value: "MacdAdxTrend", label: "MACD Trend Follower" },
    VolatilitySqueeze: { value: "VolatilitySqueeze", label: "Volatility Squeeze Breakout" },
    AiEnhancedSignal: { value: "AiEnhancedSignal", label: "AI Signal Confirmation" },
    SmcOrderBlockFvg: { value: "SmcOrderBlockFvg", label: "Smart Money Concept (SMC)" },
    SuperTrendAdx: { value: "SuperTrendAdx", label: "SuperTrend + ADX" },
    IchimokuBreakout: { value: "IchimokuBreakout", label: "Ichimoku Cloud Breakout" },
};



// This file is now complete and includes icons for a richer UI.
export const STRATEGIES_CONFIG = {

OptimizerPortfolio: {
    name: "QuantumEdge Optimizer",
    description: "A meta-strategy that analyzes signals from a pool of other strategies and only executes the highest-probability trades based on trend and confluence.",
    Icon: SparklesIcon,
    isPremium: true, // Flag for the UI
    parameters: [
      {
        name: "strategy_pool",
        type: "multiselect",
        label: "Strategy Pool",
        defaultValue: ["SmcOrderBlockFvg", "SuperTrendAdx"],
        options: Object.values(BASE_STRATEGIES), // Use all other strategies as options
        tooltip: "Select the strategies you want the Optimizer to consider."
      },
      { name: "trend_filter_period", type: "number", label: "Main Trend EMA", defaultValue: 200 },
      { name: "min_confluence", type: "number", label: "Min. Strategy Agreement", defaultValue: 1, tooltip: "How many strategies must agree before a trade is considered." },
      { name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 0.5 },
      { name: "atr_sl_multiplier", type: "number", step: 0.1, label: "SL ATR Multiplier", defaultValue: 2.0 },
    ],
  },


  EmaCrossAtr: {
    name: "Adaptive EMA Crossover",
    description: "A moving average crossover strategy where the fast EMA period adapts to market volatility using ATR.",
    Icon: ChartBarIcon,
    parameters: [
      { name: "long_period", type: "number", label: "Long EMA Period", defaultValue: 50, tooltip: "The period for the slow moving average." },
      { name: "atr_period", type: "number", label: "ATR Period", defaultValue: 14, tooltip: "The lookback period for calculating the Average True Range (ATR)." },
      { name: "atr_multiplier", type: "number", step: 0.1, label: "ATR Multiplier", defaultValue: 0.5, tooltip: "Controls how strongly volatility affects the fast EMA period." },
      { name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 1.0 },
    ],
  },
  RsiBbMeanReversion: {
    name: "RSI & Bollinger Reversion",
    description: "Enters trades on RSI extremes when the price also touches the outer Bollinger Bands, signaling potential exhaustion.",
    Icon: ScaleIcon,
    isPremium: false,
    parameters: [
      { name: "rsi_period", type: "number", label: "RSI Period", defaultValue: 14 },
      { name: "bb_period", type: "number", label: "Bollinger Bands Period", defaultValue: 20 },
      { name: "bb_std_dev", type: "number", step: 0.1, label: "BB Standard Deviation", defaultValue: 2.0 },
      { name: "oversold", type: "number", label: "RSI Oversold Level", defaultValue: 30 },
      { name: "overbought", type: "number", label: "RSI Overbought Level", defaultValue: 70 },
      { name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 1.0 },
    ],
  },
  MacdAdxTrend: {
    name: "MACD Trend Follower",
    description: "A classic MACD crossover strategy that only takes signals when the ADX indicates a strong trend.",
    Icon: ArrowsRightLeftIcon,
    parameters: [
        { name: "macd_fast", type: "number", label: "MACD Fast Period", defaultValue: 12 },
        { name: "macd_slow", type: "number", label: "MACD Slow Period", defaultValue: 26 },
        { name: "macd_signal", type: "number", label: "MACD Signal Period", defaultValue: 9 },
        { name: "adx_period", type: "number", label: "ADX Period", defaultValue: 14 },
        { name: "adx_threshold", type: "number", label: "ADX Trend Threshold", defaultValue: 25, tooltip: "ADX must be above this value to confirm a trend." },
        { name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 0.8 },
    ],
  },
  VolatilitySqueeze: {
    name: "Volatility Squeeze Breakout",
    description: "Identifies low-volatility periods and trades the subsequent explosive breakout.",
    Icon: BeakerIcon,
    parameters: [
        { name: "bb_period", type: "number", label: "Bollinger Bands Period", defaultValue: 20 },
        { name: "bb_std", type: "number", step: 0.1, label: "BB Standard Deviation", defaultValue: 2.0 },
        { name: "kc_period", type: "number", label: "Keltner Channel Period", defaultValue: 20 },
        { name: "kc_atr_mult", type: "number", step: 0.1, label: "KC ATR Multiplier", defaultValue: 1.5 },
        { name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 1.2 },
    ],
  },
  AiEnhancedSignal: {
    name: "AI Signal Confirmation",
    description: "Uses a base signal (EMA cross) and confirms it with a machine learning model for higher probability trades.",
    Icon: CpuChipIcon,
    isPremium: true,
    parameters: [
        { name: "confidence_threshold", type: "number", step: 0.01, label: "AI Confidence Threshold", defaultValue: 0.65, tooltip: "The minimum probability required from the AI model to confirm a trade." },
        { name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 0.75 },
    ],
  },
  SmcOrderBlockFvg: {
name: "Smart Money Concept (SMC)",
description: "Trades based on institutional Order Blocks and Fair Value Gaps (FVGs), aiming to enter where 'smart money' has shown interest.",
Icon: CurrencyDollarIcon, // You'll need to import this from heroicons
isPremium: true,
parameters: [
{ name: "atr_multiplier", type: "number", step: 0.1, label: "Impulse Multiplier", defaultValue: 2.5, tooltip: "How many times the ATR a candle's range must be to be considered an 'impulse'." },
{ name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 1.0 },
{ name: "atr_sl_multiplier", type: "number", step: 0.1, label: "SL ATR Multiplier", defaultValue: 1.5, tooltip: "Stop Loss distance based on ATR." },
],
},
SuperTrendAdx: {
name: "SuperTrend + ADX",
description: "A robust trend-following strategy that uses the SuperTrend indicator for signals and ADX for trend strength confirmation.",
Icon: ArrowTrendingUpIcon, // Import from heroicons
parameters: [
{ name: "st_period", type: "number", label: "SuperTrend Period", defaultValue: 10 },
{ name: "st_multiplier", type: "number", step: 0.5, label: "SuperTrend Multiplier", defaultValue: 3.0 },
{ name: "adx_period", type: "number", label: "ADX Period", defaultValue: 14 },
{ name: "adx_threshold", type: "number", label: "ADX Trend Threshold", defaultValue: 25 },
{ name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 1.0 },
{ name: "atr_sl_multiplier", type: "number", step: 0.1, label: "SL ATR Multiplier", defaultValue: 2.0 },
],
},
IchimokuBreakout: {
name: "Ichimoku Cloud Breakout",
description: "A classic Japanese trend strategy that enters trades when the price decisively breaks out of the 'Kumo' or cloud.",
Icon: CloudIcon, // Import from heroicons
parameters: [
{ name: "tenkan_period", type: "number", label: "Tenkan-sen Period", defaultValue: 9 },
{ name: "kijun_period", type: "number", label: "Kijun-sen Period", defaultValue: 26 },
{ name: "senkou_period", type: "number", label: "Senkou Span B Period", defaultValue: 52 },
{ name: "risk_percent", type: "number", step: 0.1, label: "Risk % per Trade", defaultValue: 1.0 },
{ name: "atr_sl_multiplier", type: "number", step: 0.1, label: "SL ATR Multiplier", defaultValue: 2.5 },
],
},


};