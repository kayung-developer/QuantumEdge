"""
AuraQuant - System Telemetry Service
"""
import logging
from datetime import datetime
from typing import Dict, Any

# Use a specific logger for metrics to allow for separate routing/filtering
telemetry_logger = logging.getLogger("telemetry")


class TelemetryService:
    """
    A service for capturing and logging structured telemetry data.
    In a production environment, this would be configured to output logs
    that are scraped by a monitoring system like Prometheus/Grafana or the ELK stack.
    """

    def _log_metric(self, metric_name: str, value: Any, tags: Dict[str, Any] = None):
        """
        Logs a metric in a structured key=value format for easy parsing.
        """
        tag_str = ""
        if tags:
            tag_str = " ".join([f"{k}='{v}'" for k, v in tags.items()])

        log_message = f"METRIC timestamp='{datetime.utcnow().isoformat()}' metric_name='{metric_name}' value={value} {tag_str}"
        telemetry_logger.info(log_message)

    # --- Specific Metric-Capturing Methods ---

    def record_order_latency(self, exchange: str, duration_ms: float):
        """Records the latency of an order placement round-trip."""
        self._log_metric("order.latency.ms", duration_ms, {"exchange": exchange})

    def record_fill_event(self, exchange: str, symbol: str, side: str, quantity: float, price: float):
        """Records a successful trade execution (a fill)."""
        self._log_metric("trade.fill.count", 1, {"exchange": exchange, "symbol": symbol, "side": side})
        self._log_metric("trade.fill.volume", quantity, {"exchange": exchange, "symbol": symbol, "side": side})
        self._log_metric("trade.fill.notional", quantity * price,
                         {"exchange": exchange, "symbol": symbol, "side": side})

    def record_api_request(self, endpoint: str, duration_ms: float, status_code: int):
        """Records a web API request."""
        self._log_metric("api.request.latency.ms", duration_ms, {"endpoint": endpoint, "status_code": status_code})

    def record_login(self, user_id: int, success: bool):
        """Records a user login attempt."""
        self._log_metric("user.login.attempt", 1, {"user_id": user_id, "success": str(success).lower()})


# Create a single instance
telemetry_service = TelemetryService()