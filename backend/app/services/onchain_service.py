"""
AuraQuant - On-Chain Data and DeFi Integration Service
"""
import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
from web3 import Web3, AsyncWeb3
from web3.exceptions import ContractLogicError

from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Standard ABI Snippets ---
# Application Binary Interface (ABI) is the standard way to interact with smart contracts.
# This is a minimal ABI for an ERC-20 token (like USDC, LINK, etc.)
ERC20_ABI = json.loads(
    '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]')


class OnChainService:
    def __init__(self):
        self.w3: Optional[AsyncWeb3] = None
        if settings.ETHEREUM_RPC_URL:
            self.w3 = AsyncWeb3(Web3.AsyncHTTPProvider(settings.ETHEREUM_RPC_URL))
        else:
            logger.warning("ETHEREUM_RPC_URL not configured. On-Chain Service will be disabled.")

    async def is_connected(self) -> bool:
        """Checks if the service is connected to an Ethereum node."""
        if not self.w3:
            return False
        return await self.w3.is_connected()

    async def get_native_balance(self, wallet_address: str) -> float:
        """Fetches the native currency (ETH) balance of a wallet."""
        if not await self.is_connected():
            raise ConnectionError("Not connected to Ethereum node.")

        checksum_address = self.w3.to_checksum_address(wallet_address)
        balance_wei = await self.w3.eth.get_balance(checksum_address)
        return self.w3.from_wei(balance_wei, 'ether')

    async def get_erc20_token_balance(self, token_address: str, wallet_address: str) -> Dict[str, Any]:
        """
        Fetches the balance of a specific ERC-20 token for a given wallet.
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to Ethereum node.")

        token_checksum = self.w3.to_checksum_address(token_address)
        wallet_checksum = self.w3.to_checksum_address(wallet_address)

        contract = self.w3.eth.contract(address=token_checksum, abi=ERC20_ABI)

        try:
            # Run multiple contract calls concurrently for efficiency
            symbol, decimals, balance_raw = await asyncio.gather(
                contract.functions.symbol().call(),
                contract.functions.decimals().call(),
                contract.functions.balanceOf(wallet_checksum).call()
            )

            balance_adjusted = balance_raw / (10 ** decimals)

            return {
                "token_symbol": symbol,
                "token_address": token_address,
                "balance_raw": str(balance_raw),
                "balance": balance_adjusted
            }
        except ContractLogicError as e:
            logger.error(f"Could not fetch token balance for {token_address}: {e}")
            return None

    async def track_whale_transfers(
            self, token_address: str, whale_addresses: List[str], amount_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Scans recent blocks for large ERC-20 token transfers from a list of "whale" wallets.
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to Ethereum node.")

        token_checksum = self.w3.to_checksum_address(token_address)
        contract = self.w3.eth.contract(address=token_checksum, abi=ERC20_ABI)
        decimals = await contract.functions.decimals().call()

        latest_block = await self.w3.eth.block_number

        # Scan the last 100 blocks (approx ~20 minutes on Ethereum)
        event_filter = contract.events.Transfer.create_filter(
            fromBlock=latest_block - 100,
            toBlock='latest'
        )

        large_transfers = []
        events = await event_filter.get_all_entries()

        for event in events:
            sender = event['args']['from']
            amount = event['args']['value'] / (10 ** decimals)

            if sender in whale_addresses and amount >= amount_threshold:
                large_transfers.append({
                    "transaction_hash": event['transactionHash'].hex(),
                    "block_number": event['blockNumber'],
                    "from_whale": sender,
                    "to_address": event['args']['to'],
                    "amount": amount,
                    "token_symbol": await contract.functions.symbol().call()
                })
        return large_transfers


# Create a single instance
onchain_service = OnChainService()