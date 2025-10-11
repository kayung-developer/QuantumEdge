"""
AuraQuant - API Endpoints for On-Chain and DeFi Data
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api import deps
from app.models.user import User
from app.services.onchain_service import onchain_service

router = APIRouter()

# --- Example Data for Whale Tracking ---
# In a real system, this would come from a database or a specialized analytics provider
KNOWN_WHALES = {
    "USDC": [
        "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",  # Vitalik Buterin
        "0x73BCEb1Cd57C711feCac2226092bA27182a452d1",  # Binance 8
    ]
}


@router.get("/wallet-balance/{wallet_address}")
async def get_wallet_balance(
        wallet_address: str,
        token_address: Optional[str] = None,  # Query param for a specific token
        current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    Get the ETH and (optionally) a specific ERC-20 token balance for a wallet.
    """
    if not await onchain_service.is_connected():
        raise HTTPException(status_code=503, detail="On-chain service is not available.")

    try:
        eth_balance = await onchain_service.get_native_balance(wallet_address)
        response = {"native_balance": eth_balance, "token_balance": None}

        if token_address:
            token_balance = await onchain_service.get_erc20_token_balance(token_address, wallet_address)
            response["token_balance"] = token_balance

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/whale-tracker/{token_symbol}")
async def track_whale_activity(
        token_symbol: str,
        amount_threshold: float = 100000,  # Track transfers over $100k
        current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Scans recent blocks for large transfers from known whale wallets for a given token.
    """
    if not await onchain_service.is_connected():
        raise HTTPException(status_code=503, detail="On-chain service is not available.")

    # In a real system, you would have a token symbol to address mapping
    token_map = {"USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"}
    token_address = token_map.get(token_symbol.upper())

    if not token_address:
        raise HTTPException(status_code=404, detail=f"Token symbol '{token_symbol}' not supported for tracking.")

    whale_list = KNOWN_WHALES.get(token_symbol.upper(), [])
    if not whale_list:
        return []

    try:
        transfers = await onchain_service.track_whale_transfers(token_address, whale_list, amount_threshold)
        return transfers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while tracking transfers: {e}")