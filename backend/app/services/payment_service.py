"""
AuraQuant - Payment Services Layer

This module contains the business logic for interacting with external payment gateways.
It follows a factory pattern with a protocol to ensure a consistent interface for all
payment providers, making the system extensible and maintainable.

Key Design Patterns:
- Protocol (Interface): A `PaymentGatewayProtocol` defines a common contract for all
  payment services, ensuring they all have `initialize_payment` and `verify_payment` methods.
- Factory Pattern: The `payment_factory` provides a simple, centralized way to get an
  instance of the correct payment service based on a string identifier.
- Asynchronous Operations: All external API calls are made using `httpx.AsyncClient`
  to ensure the application remains non-blocking and performant.
- Secure Configuration: API keys and secrets are securely managed via the `settings` object.
"""
import httpx
from typing import Protocol, Dict, Any, Optional
from pydantic import AnyHttpUrl

from app.core.config import settings
from app.models.user import User
from app.models.plan import Plan


class PaymentGatewayProtocol(Protocol):
    """
    A protocol defining the standard interface for all payment gateway services.
    """

    async def initialize_payment(
            self, user: User, plan: Plan, interval: str, success_url: AnyHttpUrl, cancel_url: AnyHttpUrl
    ) -> Dict[str, Any]:
        """
        Initializes a payment transaction with the provider.
        Returns a dictionary containing the authorization_url and a reference.
        """
        ...

    async def verify_payment(self, reference: str) -> Dict[str, Any]:
        """
        Verifies the status of a payment transaction with the provider.
        Returns a dictionary containing the payment status and provider details.
        """
        ...


class PaystackService:
    """
    Payment service for interacting with the Paystack API.
    """

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_payment(
            self, user: User, plan: Plan, interval: str, success_url: AnyHttpUrl, cancel_url: AnyHttpUrl
    ) -> Dict[str, Any]:
        if not self.secret_key:
            raise ValueError("Paystack secret key is not configured.")

        amount = plan.price_monthly if interval == "monthly" else plan.price_yearly
        # Paystack requires amount in the smallest currency unit (kobo for NGN, cents for USD)
        amount_in_smallest_unit = int(amount * 100)

        payload = {
            "email": user.email,
            "amount": amount_in_smallest_unit,
            "currency": plan.currency,
            "callback_url": str(success_url),
            "metadata": {
                "user_id": user.id,
                "plan_id": plan.id,
                "interval": interval,
                "full_name": user.full_name
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/transaction/initialize", headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for 4xx or 5xx status codes
            data = response.json()
            if data.get("status"):
                return {
                    "authorization_url": data["data"]["authorization_url"],
                    "reference": data["data"]["reference"]
                }
            else:
                raise Exception(f"Paystack initialization failed: {data.get('message')}")

    async def verify_payment(self, reference: str) -> Dict[str, Any]:
        if not self.secret_key:
            raise ValueError("Paystack secret key is not configured.")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/transaction/verify/{reference}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status"):
                return data["data"]  # Returns the full transaction data object from Paystack
            else:
                raise Exception(f"Paystack verification failed: {data.get('message')}")


class PayPalService:
    """
    Payment service for interacting with the PayPal API.
    """

    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = "https://api-m.sandbox.paypal.com" if settings.PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

    async def _get_access_token(self) -> str:
        if not self.client_id or not self.client_secret:
            raise ValueError("PayPal client ID or secret is not configured.")

        auth = (self.client_id, self.client_secret)
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v1/oauth2/token", headers=headers, auth=auth, data=data)
            response.raise_for_status()
            return response.json()["access_token"]

    async def initialize_payment(
            self, user: User, plan: Plan, interval: str, success_url: AnyHttpUrl, cancel_url: AnyHttpUrl
    ) -> Dict[str, Any]:
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        amount = plan.price_monthly if interval == "monthly" else plan.price_yearly
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": plan.currency,
                    "value": str(amount)
                },
                "description": f"{plan.name} - {interval.capitalize()} Subscription",
                "custom_id": f"user_id:{user.id},plan_id:{plan.id},interval:{interval}"
            }],
            "application_context": {
                "return_url": str(success_url),
                "cancel_url": str(cancel_url),
                "brand_name": settings.PROJECT_NAME,
                "user_action": "PAY_NOW"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/v2/checkout/orders", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            approve_link = next((link for link in data["links"] if link["rel"] == "approve"), None)
            if approve_link:
                return {
                    "authorization_url": approve_link["href"],
                    "reference": data["id"]  # The PayPal Order ID
                }
            else:
                raise Exception("PayPal order creation failed: No approval link found.")

    async def verify_payment(self, reference: str) -> Dict[str, Any]:
        """ 'reference' here is the PayPal order ID (token) """
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            # This endpoint captures the payment
            response = await client.post(f"{self.base_url}/v2/checkout/orders/{reference}/capture", headers=headers,
                                         json={})
            response.raise_for_status()
            data = response.json()
            # We return the full capture data which includes status, payer info, etc.
            return data


class PaymentFactory:
    """
    Factory for creating payment service instances.
    """

    def __init__(self):
        self._services = {
            "paystack": PaystackService(),
            "paypal": PayPalService(),
        }

    def get_service(self, provider_name: str) -> Optional[PaymentGatewayProtocol]:
        """
        Returns an instance of the payment service for the given provider.
        """
        provider_name = provider_name.lower()
        return self._services.get(provider_name)


# Create a single factory instance to be used throughout the application
payment_factory = PaymentFactory()