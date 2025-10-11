"""
AuraQuant - Advanced Multi-Exchange Connection Management

This module manages the lifecycle of all exchange adapter connections for the
application. It dynamically discovers, initializes, manages, and gracefully shuts
down all configured exchange connections.
"""
import asyncio
import logging
from typing import Dict, List, Optional

from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus
from app.adapters import AVAILABLE_ADAPTERS # Dynamically import all available adapters

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    A sophisticated manager for handling multiple, concurrent exchange adapter connections.
    """
    def __init__(self):
        self._adapters: Dict[str, ExchangeAdapterProtocol] = {}
        self._initialize_adapters()

    def _initialize_adapters(self):
        """
        Instantiates all available adapter classes.
        """
        for adapter_class in AVAILABLE_ADAPTERS:
            instance = adapter_class()
            self._adapters[instance.exchange_name.lower()] = instance
            logger.info(f"Discovered and instantiated adapter: {instance.exchange_name}")

    async def startup_all(self):
        """
        Concurrently connects to all available and configured adapters.
        This is called once during the application's lifespan startup event.
        """
        logger.info("Starting connection process for all configured adapters...")

        connection_tasks = []
        for name, adapter in self._adapters.items():
            # We wrap the connect call in a separate task
            task = asyncio.create_task(self._safe_connect(adapter))
            connection_tasks.append(task)

        results = await asyncio.gather(*connection_tasks)

        active_connections = [name for name, status in results if status]
        if active_connections:
            logger.info(f"Successfully connected to: {', '.join(active_connections)}")
        else:
            logger.warning("No active exchange connections were established.")

    async def _safe_connect(self, adapter: ExchangeAdapterProtocol) -> (str, bool):
        """
        A wrapper to safely attempt connection to an adapter and handle failures.
        """
        adapter_name = adapter.exchange_name
        try:
            logger.info(f"Attempting to connect to {adapter_name}...")
            await adapter.connect()
            if adapter.get_status() == ConnectionStatus.CONNECTED:
                logger.info(f"{adapter_name} connection successful.")
                return adapter_name, True
            else:
                logger.warning(f"{adapter_name} connection attempt resulted in status: {adapter.get_status()}")
                return adapter_name, False
        except Exception as e:
            logger.error(f"Failed to connect to {adapter_name}. Reason: {e}")
            return adapter_name, False

    async def shutdown_all(self):
        """
        Concurrently disconnects all active adapters.
        This is called once during the application's lifespan shutdown event.
        """
        logger.info("Shutting down all active adapter connections...")
        shutdown_tasks = [
            adapter.disconnect() for adapter in self._adapters.values()
            if adapter.get_status() == ConnectionStatus.CONNECTED
        ]
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks)
        logger.info("All active connections have been closed.")

    def get_adapter(self, name: str) -> Optional[ExchangeAdapterProtocol]:
        """
        Retrieves a specific, active adapter instance by name.

        Args:
            name: The name of the exchange (case-insensitive).

        Returns:
            An instance of the adapter if it exists and is connected, otherwise None.
        """
        adapter = self._adapters.get(name.lower())
        if adapter and adapter.get_status() == ConnectionStatus.CONNECTED:
            return adapter
        return None

    def get_all_active_adapters(self) -> List[ExchangeAdapterProtocol]:
        """
        Returns a list of all currently active and connected adapter instances.
        """
        return [
            adapter for adapter in self._adapters.values()
            if adapter.get_status() == ConnectionStatus.CONNECTED
        ]

# Create a single, global instance of the new connection manager.
# This will be imported by the main application and services.
connection_manager = ConnectionManager()