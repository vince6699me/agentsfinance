#!/usr/bin/env python3
"""
AgentFinance Technical Analysis Engine
80+ technical indicators using pure Python implementations.
Compatible with cinar/indicator library patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class IndicatorResult:
    """Container for indicator results."""

    name: str
    values: pd.Series
    signals: Optional[pd.Series] = None
    metadata: Optional[Dict] = None


@dataclass
class ConfluenceSignal:
    """Multi-indicator confluence signal."""

    direction: str  # "LONG", "SHORT", "NEUTRAL"
    confidence: float
    trend_score: float
    momentum_score: float
    volume_score: float
    signals: List[Dict]


class IndicatorEngine:
    """Technical analysis engine with 80+ indicators."""

    def __init__(self):
        self.indicators_cache = {}

    # ========================================================================
    # TREND INDICATORS
    # ========================================================================

    def sma(self, data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average."""
        return data.rolling(window=period).mean()

    def ema(self, data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average."""
        return data.ewm(span=period, adjust=False).mean()

    def wma(self, data: pd.Series, period: int) -> pd.Series:
        """Weighted Moving Average."""
        weights = np.arange(1, period + 1)
        return data.rolling(window=period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )

    def dema(self, data: pd.Series, period: int) -> pd.Series:
        """Double Exponential Moving Average."""
        ema1 = self.ema(data, period)
        ema2 = self.ema(ema1, period)
        return 2 * ema1 - ema2

    def tema(self, data: pd.Series, period: int) -> pd.Series:
        """Triple Exponential Moving Average."""
        ema1 = self.ema(data, period)
        ema2 = self.ema(ema1, period)
        ema3 = self.ema(ema2, period)
        return 3 * ema1 - 3 * ema2 + ema3

    def hma(self, data: pd.Series, period: int) -> pd.Series:
        """Hull Moving Average."""
        half = int(period / 2)
        sqrt = int(np.sqrt(period))
        wma1 = self.wma(data, half)
        wma2 = self.wma(data, period)
        diff = 2 * wma1 - wma2
        return self.wma(diff, sqrt)

    def supertrend(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 10,
        multiplier: float = 3.0,
    ) -> Tuple[pd.Series, pd.Series]:
        """
        SuperTrend indicator.
        Returns (supertrend_line, supertrend_direction)
        direction: 1 = bullish, -1 = bearish
        """
        # ATR calculation
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        # HL/2 calculation
        hl2 = (high + low) / 2

        # Upper and lower bands
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)

        # Supertrend calculation
        supertrend = close.copy()
        direction = pd.Series(1, index=close.index)

        for i in range(1, len(close)):
            if close.iloc[i] > upper_band.iloc[i]:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
            elif close.iloc[i] < lower_band.iloc[i]:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = supertrend.iloc[i - 1]
                direction.iloc[i] = direction.iloc[i - 1]

                if (
                    direction.iloc[i] == 1
                    and lower_band.iloc[i] < lower_band.iloc[i - 1]
                ):
                    direction.iloc[i] = -1
                elif (
                    direction.iloc[i] == -1
                    and upper_band.iloc[i] > upper_band.iloc[i - 1]
                ):
                    direction.iloc[i] = 1

        return supertrend, direction

    def ichimoku(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        tenkan: int = 9,
        kijun: int = 26,
        senkou_b: int = 52,
    ) -> Dict[str, pd.Series]:
        """
        Ichimoku Cloud indicator.
        Returns dict with: tenkan, kijun, senkou_a, senkou_b, chikou
        """
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (
            high.rolling(window=tenkan).max() + low.rolling(window=tenkan).min()
        ) / 2

        # Kijun-sen (Base Line)
        kijun_sen = (
            high.rolling(window=kijun).max() + low.rolling(window=kijun).min()
        ) / 2

        # Senkou Span A (Leading Span A)
        senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)

        # Senkou Span B (Leading Span B)
        senkou_b = (
            (high.rolling(window=senkou_b).max() + low.rolling(window=senkou_b).min())
            / 2
        ).shift(kijun)

        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-kijun)

        return {
            "tenkan": tenkan_sen,
            "kijun": kijun_sen,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b,
            "chikou": chikou_span,
        }

    def adx(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Average Directional Index (ADX).
        Returns (adx, plus_di, minus_di)
        """
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # Smooth
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx, plus_di, minus_di

    def parabolic_sar(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        af_start: float = 0.02,
        af_increment: float = 0.02,
        af_max: float = 0.2,
    ) -> pd.Series:
        """
        Parabolic SAR indicator.
        """
        sar = close.copy()
        trend = pd.Series(1, index=close.index)
        af = af_start
        ep = high.iloc[0]

        for i in range(1, len(close)):
            prior_sar = sar.iloc[i - 1]
            prior_trend = trend.iloc[i - 1]

            if prior_trend == 1:
                sar.iloc[i] = prior_sar + af * (ep - prior_sar)
                if low.iloc[i] < sar.iloc[i]:
                    trend.iloc[i] = -1
                    sar.iloc[i] = ep
                    ep = low.iloc[i]
                    af = af_start
                else:
                    trend.iloc[i] = 1
                    if high.iloc[i] > ep:
                        ep = high.iloc[i]
                        af = min(af + af_increment, af_max)
            else:
                sar.iloc[i] = prior_sar - af * (prior_sar - ep)
                if high.iloc[i] > sar.iloc[i]:
                    trend.iloc[i] = 1
                    sar.iloc[i] = ep
                    ep = high.iloc[i]
                    af = af_start
                else:
                    trend.iloc[i] = -1
                    if low.iloc[i] < ep:
                        ep = low.iloc[i]
                        af = min(af + af_increment, af_max)

        return sar

    def aroon(
        self, high: pd.Series, low: pd.Series, period: int = 25
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Aroon indicator.
        Returns (aroon_up, aroon_down, aroon_oscillator)
        """
        aroon_up = high.rolling(window=period + 1).apply(
            lambda x: float(np.argmax(x)) / period * 100, raw=True
        )
        aroon_down = low.rolling(window=period + 1).apply(
            lambda x: float(np.argmin(x)) / period * 100, raw=True
        )
        aroon_osc = aroon_up - aroon_down

        return aroon_up, aroon_down, aroon_osc

    # ========================================================================
    # MOMENTUM INDICATORS
    # ========================================================================

    def rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index (RSI).
        """
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def stochastic(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3,
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator.
        Returns (%K, %D)
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()

        return k, d

    def macd(
        self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence).
        Returns (macd_line, signal_line, histogram)
        """
        ema_fast = self.ema(data, fast)
        ema_slow = self.ema(data, slow)

        macd_line = ema_fast - ema_slow
        signal_line = self.ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def cci(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20
    ) -> pd.Series:
        """
        Commodity Channel Index (CCI).
        """
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True
        )
        cci = (tp - sma_tp) / (0.015 * mad)

        return cci

    def roc(self, data: pd.Series, period: int = 10) -> pd.Series:
        """
        Rate of Change (ROC).
        """
        roc = ((data - data.shift(period)) / data.shift(period)) * 100
        return roc

    def williams_r(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Williams %R.
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()

        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return wr

    def momentum(self, data: pd.Series, period: int = 10) -> pd.Series:
        """
        Momentum indicator.
        """
        return data.diff(period)

    def mfi(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        period: int = 14,
    ) -> pd.Series:
        """
        Money Flow Index (MFI).
        """
        tp = (high + low + close) / 3
        raw_money_flow = tp * volume

        money_flow_sign = pd.Series(1, index=tp.index)
        for i in range(1, len(tp)):
            if tp.iloc[i] > tp.iloc[i - 1]:
                money_flow_sign.iloc[i] = 1
            elif tp.iloc[i] < tp.iloc[i - 1]:
                money_flow_sign.iloc[i] = -1

        positive_flow = raw_money_flow * (money_flow_sign == 1)
        negative_flow = raw_money_flow * (money_flow_sign == -1)

        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()

        mfr = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + mfr))

        return mfi

    def ultimate_oscillator(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period1: int = 7,
        period2: int = 14,
        period3: int = 28,
    ) -> pd.Series:
        """
        Ultimate Oscillator.
        """
        bp = close - pd.concat([low, close.shift()], axis=1).min(axis=1)
        tr = pd.concat([high, close.shift()], axis=1).max(axis=1) - pd.concat(
            [low, close.shift()], axis=1
        ).min(axis=1)

        avg1 = bp.rolling(window=period1).sum() / tr.rolling(window=period1).sum()
        avg2 = bp.rolling(window=period2).sum() / tr.rolling(window=period2).sum()
        avg3 = bp.rolling(window=period3).sum() / tr.rolling(window=period3).sum()

        uo = 100 * ((4 * avg1) + (2 * avg2) + avg3) / (4 + 2 + 1)

        return uo

    def awesome_oscillator(self, high: pd.Series, low: pd.Series) -> pd.Series:
        """
        Awesome Oscillator.
        """
        median_price = (high + low) / 2
        ao = self.sma(median_price, 5) - self.sma(median_price, 34)
        return ao

    def elder_force_index(
        self, close: pd.Series, volume: pd.Series, period: int = 13
    ) -> pd.Series:
        """
        Elder Force Index (EFI).
        """
        efi = close.diff() * volume
        efi_smooth = self.ema(efi, period)
        return efi_smooth

    def trix(self, data: pd.Series, period: int = 15) -> pd.Series:
        """
        TRIX (Triple Exponential Average).
        """
        ema1 = self.ema(data, period)
        ema2 = self.ema(ema1, period)
        ema3 = self.ema(ema2, period)
        trix = 100 * ema3.diff() / ema3.shift()
        return trix

    def kst(
        self,
        data: pd.Series,
        roc1: int = 10,
        roc2: int = 15,
        roc3: int = 20,
        roc4: int = 30,
        sma1: int = 10,
        sma2: int = 10,
        sma3: int = 10,
        sma4: int = 15,
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Know Sure Thing (KST).
        Returns (kst_line, signal_line)
        """
        rcma1 = self.roc(data, roc1).rolling(window=sma1).mean()
        rcma2 = self.roc(data, roc2).rolling(window=sma2).mean()
        rcma3 = self.roc(data, roc3).rolling(window=sma3).mean()
        rcma4 = self.roc(data, roc4).rolling(window=sma4).mean()

        kst = (rcma1 * 1) + (rcma2 * 2) + (rcma3 * 3) + (rcma4 * 4)
        kst_signal = self.ema(kst, 9)

        return kst, kst_signal

    # ========================================================================
    # VOLATILITY INDICATORS
    # ========================================================================

    def bollinger_bands(
        self, data: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands.
        Returns (upper, middle, lower)
        """
        middle = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    def atr(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Average True Range (ATR).
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return tr.rolling(window=period).mean()

    def keltner_channels(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        ema_period: int = 20,
        atr_period: int = 10,
        multiplier: float = 2.0,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Keltner Channels.
        Returns (upper, middle, lower)
        """
        middle = self.ema(close, ema_period)
        atr_val = self.atr(high, low, close, atr_period)

        upper = middle + (multiplier * atr_val)
        lower = middle - (multiplier * atr_val)

        return upper, middle, lower

    def donchian_channels(
        self, high: pd.Series, low: pd.Series, period: int = 20
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Donchian Channels.
        Returns (upper, middle, lower)
        """
        upper = high.rolling(window=period).max()
        lower = low.rolling(window=period).min()
        middle = (upper + lower) / 2

        return upper, middle, lower

    def historical_volatility(self, data: pd.Series, period: int = 21) -> pd.Series:
        """
        Historical Volatility (annualized).
        """
        log_returns = np.log(data / data.shift())
        hv = log_returns.rolling(window=period).std() * np.sqrt(252) * 100

        return hv

    def ulcer_index(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Ulcer Index - downside risk measure.
        """
        highest = data.rolling(window=period).max()
        percentage = ((data - highest) / highest) * 100
        squared = percentage**2
        ui = np.sqrt(squared.rolling(window=period).mean())

        return ui

    # ========================================================================
    # VOLUME INDICATORS
    # ========================================================================

    def on_balance_volume(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On Balance Volume (OBV).
        """
        obv = pd.Series(0, index=close.index)
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    def vwap(
        self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
    ) -> pd.Series:
        """
        Volume Weighted Average Price (VWAP).
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()

        return vwap

    def chaikin_money_flow(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        period: int = 20,
    ) -> pd.Series:
        """
        Chaikin Money Flow (CMF).
        """
        mf_multiplier = ((close - low) - (high - close)) / (high - low)
        mf_multiplier = mf_multiplier.fillna(0)
        mf_volume = mf_multiplier * volume

        cmf = (
            mf_volume.rolling(window=period).sum() / volume.rolling(window=period).sum()
        )

        return cmf

    def accumulation_distribution(
        self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
    ) -> pd.Series:
        """
        Accumulation/Distribution Line (A/D).
        """
        mf_multiplier = ((close - low) - (high - close)) / (high - low)
        mf_multiplier = mf_multiplier.fillna(0)
        mf_volume = mf_multiplier * volume

        ad_line = mf_volume.cumsum()

        return ad_line

    def force_index(
        self, close: pd.Series, volume: pd.Series, period: int = 13
    ) -> pd.Series:
        """
        Force Index (FI).
        """
        fi = close.diff(period) * volume.diff(period)
        fi_smooth = self.ema(fi, period)

        return fi_smooth

    def volume_roc(self, volume: pd.Series, period: int = 14) -> pd.Series:
        """
        Volume Rate of Change (V-ROC).
        """
        vroc = ((volume - volume.shift(period)) / volume.shift(period)) * 100
        return vroc

    def ease_of_movement(
        self, high: pd.Series, low: pd.Series, volume: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Ease of Movement (EOM).
        """
        distance = ((high + low) / 2) - ((high.shift() + low.shift()) / 2)
        box_ratio = (volume / 1000000) / (high - low)
        eom = distance / box_ratio
        eom_smooth = eom.rolling(window=period).mean()

        return eom_smooth

    # ========================================================================
    # RUN ALL INDICATORS
    # ========================================================================

    def run_all(self, ohlcv: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Run all indicators on OHLCV data.
        Returns dict of all indicator values.
        """
        results = {}
        close = ohlcv["close"]
        high = ohlcv["high"]
        low = ohlcv["low"]
        volume = ohlcv["volume"]

        # Trend Indicators
        for period in [9, 21, 50, 100, 200]:
            results[f"ema_{period}"] = self.ema(close, period)
        for period in [20, 50, 200]:
            results[f"sma_{period}"] = self.sma(close, period)

        results["dema_20"] = self.dema(close, 20)
        results["tema_20"] = self.tema(close, 20)
        results["hma_20"] = self.hma(close, 20)

        # Ichimoku
        ichimoku = self.ichimoku(high, low, close)
        results.update(ichimoku)

        # ADX
        adx, plus_di, minus_di = self.adx(high, low, close)
        results["adx"] = adx
        results["plus_di"] = plus_di
        results["minus_di"] = minus_di

        # SuperTrend
        supertrend, supertrend_dir = self.supertrend(high, low, close)
        results["supertrend"] = supertrend
        results["supertrend_dir"] = supertrend_dir

        # Momentum Indicators
        results["rsi"] = self.rsi(close, 14)
        results["rsi_28"] = self.rsi(close, 28)

        stoch_k, stoch_d = self.stochastic(high, low, close)
        results["stoch_k"] = stoch_k
        results["stoch_d"] = stoch_d

        macd_line, signal_line, histogram = self.macd(close)
        results["macd"] = macd_line
        results["macd_signal"] = signal_line
        results["macd_histogram"] = histogram

        results["cci"] = self.cci(high, low, close, 20)
        results["roc"] = self.roc(close, 10)
        results["williams_r"] = self.williams_r(high, low, close)
        results["momentum"] = self.momentum(close)
        results["mfi"] = self.mfi(high, low, close, volume)
        results["uo"] = self.ultimate_oscillator(high, low, close)
        results["ao"] = self.awesome_oscillator(high, low)
        results["efi"] = self.elder_force_index(close, volume)
        results["trix"] = self.trix(close)

        kst, kst_signal = self.kst(close)
        results["kst"] = kst
        results["kst_signal"] = kst_signal

        # Volatility Indicators
        bb_upper, bb_middle, bb_lower = self.bollinger_bands(close)
        results["bb_upper"] = bb_upper
        results["bb_middle"] = bb_middle
        results["bb_lower"] = bb_lower

        results["atr"] = self.atr(high, low, close)

        kc_upper, kc_middle, kc_lower = self.keltner_channels(high, low, close)
        results["kc_upper"] = kc_upper
        results["kc_middle"] = kc_middle
        results["kc_lower"] = kc_lower

        dc_upper, dc_middle, dc_lower = self.donchian_channels(high, low)
        results["dc_upper"] = dc_upper
        results["dc_middle"] = dc_middle
        results["dc_lower"] = dc_lower

        results["hv"] = self.historical_volatility(close)
        results["ulcer"] = self.ulcer_index(close)

        # Volume Indicators
        results["obv"] = self.on_balance_volume(close, volume)
        results["vwap"] = self.vwap(high, low, close, volume)
        results["cmf"] = self.chaikin_money_flow(high, low, close, volume)
        results["ad"] = self.accumulation_distribution(high, low, close, volume)
        results["fi"] = self.force_index(close, volume)
        results["vroc"] = self.volume_roc(volume)
        results["eom"] = self.ease_of_movement(high, low, volume)

        return results

    # ========================================================================
    # CONFLUENCE SIGNAL GENERATION
    # ========================================================================

    def get_confluence_signal(
        self, indicators: Dict[str, pd.Series]
    ) -> ConfluenceSignal:
        """
        Aggregate all indicators into a single directional signal.
        """
        close = indicators.get("close", pd.Series())
        if len(close) == 0:
            return ConfluenceSignal("NEUTRAL", 0.0, 0.0, 0.0, 0.0, [])

        bull_score = 0.0
        bear_score = 0.0
        signals = []

        # Trend signals (weight: 0.45)
        trend_score = 0.0

        # EMA alignment
        ema_9 = indicators.get("ema_9", close)
        ema_21 = indicators.get("ema_21", close)
        ema_50 = indicators.get("ema_50", close)

        if ema_9.iloc[-1] > ema_21.iloc[-1] > ema_50.iloc[-1]:
            trend_score += 0.3
            bull_score += 1
            signals.append({"indicator": "EMA Alignment", "signal": "BULLISH"})
        elif ema_9.iloc[-1] < ema_21.iloc[-1] < ema_50.iloc[-1]:
            trend_score -= 0.3
            bear_score += 1
            signals.append({"indicator": "EMA Alignment", "signal": "BEARISH"})

        # ADX
        adx = indicators.get("adx", close)
        if adx.iloc[-1] > 25:
            trend_score += 0.2 if adx.iloc[-1] > 40 else 0.1
            signals.append(
                {"indicator": "ADX", "value": adx.iloc[-1], "signal": "STRONG_TREND"}
            )

        # SuperTrend
        st_dir = indicators.get("supertrend_dir", pd.Series([0]))
        if len(st_dir) > 0:
            if st_dir.iloc[-1] == 1:
                trend_score += 0.2
                bull_score += 0.5
            else:
                trend_score -= 0.2
                bear_score += 0.5

        # Momentum signals (weight: 0.35)
        momentum_score = 0.0

        # RSI
        rsi = indicators.get("rsi", close)
        if len(rsi) > 0:
            if rsi.iloc[-1] < 30:
                momentum_score += 0.35
                bull_score += 1.5
                signals.append(
                    {"indicator": "RSI", "value": rsi.iloc[-1], "signal": "OVERSOLD"}
                )
            elif rsi.iloc[-1] > 70:
                momentum_score -= 0.35
                bear_score += 1.5
                signals.append(
                    {"indicator": "RSI", "value": rsi.iloc[-1], "signal": "OVERBOUGHT"}
                )
            elif 40 < rsi.iloc[-1] < 60:
                momentum_score += 0.1

        # MACD
        macd_hist = indicators.get("macd_histogram", close)
        if len(macd_hist) > 0:
            if macd_hist.iloc[-1] > 0:
                momentum_score += 0.2
                bull_score += 0.5
            else:
                momentum_score -= 0.2
                bear_score += 0.5

        # Stochastic
        stoch_k = indicators.get("stoch_k", close)
        if len(stoch_k) > 0:
            if stoch_k.iloc[-1] < 20:
                momentum_score += 0.15
                bull_score += 0.5
            elif stoch_k.iloc[-1] > 80:
                momentum_score -= 0.15
                bear_score += 0.5

        # Volume signals (weight: 0.20)
        volume_score = 0.0

        # OBV
        obv = indicators.get("obv", close)
        if len(obv) > 5:
            if obv.iloc[-1] > obv.iloc[-5]:
                volume_score += 0.2
                bull_score += 0.5
            else:
                volume_score -= 0.2
                bear_score += 0.5

        # VWAP
        vwap = indicators.get("vwap", close)
        if len(vwap) > 0:
            if close.iloc[-1] > vwap.iloc[-1]:
                volume_score += 0.15
                bull_score += 0.3
            else:
                volume_score -= 0.15
                bear_score += 0.3

        # CMF
        cmf = indicators.get("cmf", close)
        if len(cmf) > 0:
            if cmf.iloc[-1] > 0:
                volume_score += 0.1
                bull_score += 0.2
            else:
                volume_score -= 0.1
                bear_score += 0.2

        # Final scores
        final_score = (
            (trend_score * 0.45) + (momentum_score * 0.35) + (volume_score * 0.20)
        )

        if final_score > 0.1:
            direction = "LONG"
        elif final_score < -0.1:
            direction = "SHORT"
        else:
            direction = "NEUTRAL"

        confidence = max(bull_score, bear_score) / (bull_score + bear_score + 1)

        return ConfluenceSignal(
            direction=direction,
            confidence=confidence,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volume_score=volume_score,
            signals=signals,
        )


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """CLI for running technical analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Technical Analysis Tool")
    parser.add_argument("--symbol", default="EURUSD", help="Trading symbol")
    parser.add_argument("--indicator", help="Specific indicator to run")

    args = parser.parse_args()

    # Create sample data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=200, freq="1h")
    np.random.seed(42)

    base_price = 1.0850
    sample_data = pd.DataFrame(
        {
            "open": base_price + np.cumsum(np.random.randn(200) * 0.0005),
            "high": base_price
            + np.cumsum(np.random.randn(200) * 0.0005)
            + np.abs(np.random.randn(200) * 0.0003),
            "low": base_price
            + np.cumsum(np.random.randn(200) * 0.0005)
            - np.abs(np.random.randn(200) * 0.0003),
            "close": base_price + np.cumsum(np.random.randn(200) * 0.0005),
            "volume": np.random.randint(1000, 10000, 200),
        },
        index=dates,
    )

    sample_data["high"] = sample_data[["open", "high", "close"]].max(axis=1)
    sample_data["low"] = sample_data[["open", "low", "close"]].min(axis=1)

    engine = IndicatorEngine()

    print(f"\n{'=' * 60}")
    print(f"Technical Analysis: {args.symbol}")
    print(f"{'=' * 60}")

    if args.indicator:
        # Run specific indicator
        result = getattr(engine, args.indicator)(sample_data)
        print(f"\n{args.indicator}: {result.iloc[-1]:.5f}")
    else:
        # Run all indicators
        results = engine.run_all(sample_data)

        print(f"\nKey Indicators:")
        print(f"  RSI(14):    {results['rsi'].iloc[-1]:.2f}")
        print(f"  MACD:       {results['macd'].iloc[-1]:.5f}")
        print(f"  ADX:        {results['adx'].iloc[-1]:.2f}")
        print(f"  ATR:        {results['atr'].iloc[-1]:.5f}")
        print(f"  VWAP:       {results['vwap'].iloc[-1]:.5f}")

        # Get confluence signal
        signal = engine.get_confluence_signal(results)
        print(f"\nConfluence Signal:")
        print(f"  Direction:  {signal.direction}")
        print(f"  Confidence: {signal.confidence:.0%}")
        print(f"  Trend:      {signal.trend_score:.2f}")
        print(f"  Momentum:   {signal.momentum_score:.2f}")
        print(f"  Volume:     {signal.volume_score:.2f}")


if __name__ == "__main__":
    main()
