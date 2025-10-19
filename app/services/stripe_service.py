"""
Stripe service with mock/test/live mode support.

Modes:
- mock: Simulates Stripe API for development/testing without actual API calls
- test: Uses Stripe test mode with real API calls (requires test keys)
- live: Uses Stripe live mode for production (requires live keys)

Enable/disable via config: stripe_enabled: true/false
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
import hmac


class MockStripeAPI:
    """
    Mock Stripe API that simulates responses without making real API calls.
    Perfect for development and testing without Stripe credentials.
    """

    def __init__(self):
        self.customers = {}
        self.subscriptions = {}
        self.checkout_sessions = {}
        self.events = []

    def create_checkout_session(
        self,
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = 'subscription'
    ) -> Dict[str, Any]:
        """Create a mock checkout session"""
        session_id = f"cs_test_{secrets.token_hex(16)}"

        session = {
            'id': session_id,
            'object': 'checkout.session',
            'customer_email': customer_email,
            'mode': mode,
            'status': 'open',
            'url': f'https://checkout.stripe.com/mock/{session_id}',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [{'price': price_id, 'quantity': 1}],
            'metadata': {},
        }

        self.checkout_sessions[session_id] = session
        return session

    def create_customer(self, email: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a mock customer"""
        customer_id = f"cus_mock_{secrets.token_hex(8)}"

        customer = {
            'id': customer_id,
            'object': 'customer',
            'email': email,
            'created': int(datetime.utcnow().timestamp()),
            'metadata': metadata or {},
        }

        self.customers[customer_id] = customer
        return customer

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a mock subscription"""
        subscription_id = f"sub_mock_{secrets.token_hex(8)}"

        subscription = {
            'id': subscription_id,
            'object': 'subscription',
            'customer': customer_id,
            'status': 'active',
            'current_period_start': int(datetime.utcnow().timestamp()),
            'current_period_end': int((datetime.utcnow() + timedelta(days=30)).timestamp()),
            'items': {
                'data': [{'price': {'id': price_id}}]
            },
            'metadata': metadata or {},
        }

        self.subscriptions[subscription_id] = subscription
        return subscription

    def complete_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """
        Simulate completing a checkout session (for testing).
        This would normally happen when user completes payment.
        """
        session = self.checkout_sessions.get(session_id)
        if not session:
            raise ValueError(f"Checkout session {session_id} not found")

        # Create customer
        customer = self.create_customer(session['customer_email'])

        # Create subscription
        price_id = session['line_items'][0]['price']
        subscription = self.create_subscription(customer['id'], price_id)

        # Update session
        session['status'] = 'complete'
        session['customer'] = customer['id']
        session['subscription'] = subscription['id']
        session['payment_status'] = 'paid'

        # Create event
        event = self.create_event('checkout.session.completed', session)

        return session

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a mock subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        subscription['status'] = 'canceled'
        subscription['canceled_at'] = int(datetime.utcnow().timestamp())

        # Create event
        event = self.create_event('customer.subscription.deleted', subscription)

        return subscription

    def create_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock webhook event"""
        event = {
            'id': f"evt_mock_{secrets.token_hex(8)}",
            'object': 'event',
            'type': event_type,
            'data': {'object': data},
            'created': int(datetime.utcnow().timestamp()),
        }

        self.events.append(event)
        return event

    def construct_event(self, payload: bytes, sig_header: str, secret: str) -> Dict[str, Any]:
        """
        Mock webhook signature verification.
        In mock mode, we just parse the payload without real verification.
        """
        import json
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            raise ValueError("Invalid payload")


class StripeService:
    """
    Unified Stripe service that works in mock, test, or live mode.

    Usage:
        service = StripeService(app)
        session = service.create_checkout_session(...)
    """

    def __init__(self, app=None):
        self.app = app
        self.mode = None
        self.enabled = False
        self._stripe_module = None
        self._mock_api = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.enabled = app.config.get('stripe_enabled', False)
        self.mode = app.config.get('stripe_mode', 'mock')

        if not self.enabled:
            return

        if self.mode == 'mock':
            self._mock_api = MockStripeAPI()
        else:
            # Only import stripe module if using test/live mode
            try:
                import stripe
                self._stripe_module = stripe
                stripe.api_key = app.config.get('stripe_secret_key')
            except ImportError:
                raise ImportError(
                    "Stripe SDK not installed. Install with: pip install -e '.[stripe]'"
                )

    def is_enabled(self) -> bool:
        """Check if Stripe is enabled"""
        return self.enabled

    def get_publishable_key(self) -> Optional[str]:
        """Get publishable key for frontend"""
        if not self.enabled:
            return None
        return self.app.config.get('stripe_publishable_key')

    def create_checkout_session(
        self,
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = 'subscription'
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session.
        Works in mock, test, and live modes.
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not enabled")

        if self.mode == 'mock':
            return self._mock_api.create_checkout_session(
                customer_email=customer_email,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                mode=mode
            )
        else:
            # Real Stripe API call
            session = self._stripe_module.checkout.Session.create(
                customer_email=customer_email,
                payment_method_types=['card'],
                line_items=[{'price': price_id, 'quantity': 1}],
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify and construct webhook event.
        In mock mode, skips signature verification.
        """
        if not self.enabled:
            raise RuntimeError("Stripe is not enabled")

        webhook_secret = self.app.config.get('stripe_webhook_secret')

        if self.mode == 'mock':
            return self._mock_api.construct_event(payload, sig_header, webhook_secret)
        else:
            # Real Stripe webhook verification
            try:
                event = self._stripe_module.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
                return event
            except self._stripe_module.error.SignatureVerificationError:
                raise ValueError("Invalid webhook signature")

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        if not self.enabled:
            return None

        if self.mode == 'mock':
            return self._mock_api.subscriptions.get(subscription_id)
        else:
            try:
                return self._stripe_module.Subscription.retrieve(subscription_id)
            except self._stripe_module.error.StripeError:
                return None

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        if not self.enabled:
            raise RuntimeError("Stripe is not enabled")

        if self.mode == 'mock':
            return self._mock_api.cancel_subscription(subscription_id)
        else:
            return self._stripe_module.Subscription.delete(subscription_id)

    # Helper methods for testing
    def _complete_mock_checkout(self, session_id: str) -> Dict[str, Any]:
        """Helper for testing: complete a mock checkout session"""
        if self.mode != 'mock':
            raise RuntimeError("This method only works in mock mode")
        return self._mock_api.complete_checkout_session(session_id)

    def _get_mock_api(self) -> MockStripeAPI:
        """Get mock API instance (for testing)"""
        if self.mode != 'mock':
            raise RuntimeError("Mock API only available in mock mode")
        return self._mock_api


# Global instance (initialized in app factory)
stripe_service = StripeService()
