"""
Comprehensive tests for Stripe integration.

Tests cover:
- Mock mode functionality (default)
- Test mode with real Stripe API (requires test keys)
- Live mode checks (warning only, no actual live API calls)
- Checkout flow
- Webhook handling
- Subscription management
"""
import pytest
import json
from datetime import datetime, timedelta
from app.services.stripe_service import StripeService, MockStripeAPI
from app.models import User


class TestMockStripeAPI:
    """Test the MockStripeAPI directly"""

    def test_create_customer(self, mock_stripe_api):
        """Test creating a mock customer"""
        customer = mock_stripe_api.create_customer(
            email='test@example.com',
            metadata={'source': 'test'}
        )

        assert customer['id'].startswith('cus_mock_')
        assert customer['email'] == 'test@example.com'
        assert customer['metadata']['source'] == 'test'

    def test_create_subscription(self, mock_stripe_api):
        """Test creating a mock subscription"""
        customer = mock_stripe_api.create_customer('test@example.com')

        subscription = mock_stripe_api.create_subscription(
            customer_id=customer['id'],
            price_id='price_test_basic',
            metadata={'plan': 'basic'}
        )

        assert subscription['id'].startswith('sub_mock_')
        assert subscription['customer'] == customer['id']
        assert subscription['status'] == 'active'
        assert subscription['items']['data'][0]['price']['id'] == 'price_test_basic'

    def test_create_checkout_session(self, mock_stripe_api):
        """Test creating a mock checkout session"""
        session = mock_stripe_api.create_checkout_session(
            customer_email='test@example.com',
            price_id='price_test_basic',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
            mode='subscription'
        )

        assert session['id'].startswith('cs_test_')
        assert session['customer_email'] == 'test@example.com'
        assert session['mode'] == 'subscription'
        assert session['status'] == 'open'
        assert session['url'].startswith('https://checkout.stripe.com/mock/')

    def test_complete_checkout_session(self, mock_stripe_api):
        """Test completing a checkout session (simulating payment)"""
        session = mock_stripe_api.create_checkout_session(
            customer_email='test@example.com',
            price_id='price_test_basic',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )

        # Complete the session
        completed_session = mock_stripe_api.complete_checkout_session(session['id'])

        assert completed_session['status'] == 'complete'
        assert completed_session['payment_status'] == 'paid'
        assert completed_session['customer'].startswith('cus_mock_')
        assert completed_session['subscription'].startswith('sub_mock_')

    def test_cancel_subscription(self, mock_stripe_api):
        """Test canceling a subscription"""
        customer = mock_stripe_api.create_customer('test@example.com')
        subscription = mock_stripe_api.create_subscription(
            customer_id=customer['id'],
            price_id='price_test_basic'
        )

        # Cancel the subscription
        canceled_sub = mock_stripe_api.cancel_subscription(subscription['id'])

        assert canceled_sub['status'] == 'canceled'
        assert 'canceled_at' in canceled_sub

    def test_webhook_event_creation(self, mock_stripe_api):
        """Test creating webhook events"""
        session = mock_stripe_api.create_checkout_session(
            customer_email='test@example.com',
            price_id='price_test_basic',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )

        event = mock_stripe_api.create_event('checkout.session.completed', session)

        assert event['id'].startswith('evt_mock_')
        assert event['type'] == 'checkout.session.completed'
        assert event['data']['object'] == session


class TestStripeService:
    """Test the StripeService in different modes"""

    def test_service_disabled_by_default(self, app):
        """Test that Stripe is disabled by default"""
        service = StripeService(app)

        assert not service.is_enabled()
        assert service.get_publishable_key() is None

    def test_service_mock_mode(self, stripe_service_mock):
        """Test StripeService in mock mode"""
        assert stripe_service_mock.is_enabled()
        assert stripe_service_mock.mode == 'mock'
        assert stripe_service_mock.get_publishable_key() == 'pk_test_mock'

    def test_create_checkout_session_mock(self, stripe_service_mock):
        """Test creating checkout session in mock mode"""
        session = stripe_service_mock.create_checkout_session(
            customer_email='test@example.com',
            price_id='price_test_basic',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )

        assert session['id'].startswith('cs_test_')
        assert session['customer_email'] == 'test@example.com'

    def test_webhook_event_construction_mock(self, stripe_service_mock, stripe_webhook_payload):
        """Test webhook event construction in mock mode"""
        event = stripe_service_mock.construct_webhook_event(
            stripe_webhook_payload,
            sig_header='mock_signature'
        )

        assert event['type'] == 'checkout.session.completed'
        assert 'data' in event

    def test_get_subscription_mock(self, stripe_service_mock, mock_stripe_subscription):
        """Test getting subscription details in mock mode"""
        subscription = stripe_service_mock.get_subscription(
            mock_stripe_subscription['id']
        )

        assert subscription is not None
        assert subscription['id'] == mock_stripe_subscription['id']
        assert subscription['status'] == 'active'

    def test_cancel_subscription_mock(self, stripe_service_mock, mock_stripe_subscription):
        """Test canceling subscription in mock mode"""
        canceled_sub = stripe_service_mock.cancel_subscription(
            mock_stripe_subscription['id']
        )

        assert canceled_sub['status'] == 'canceled'


class TestPricingPage:
    """Test the pricing page"""

    def test_pricing_page_disabled_when_stripe_off(self, client):
        """Test that pricing page redirects when Stripe is disabled"""
        response = client.get('/pricing/')

        # Should redirect since Stripe is disabled by default
        assert response.status_code == 302

    def test_pricing_page_with_stripe_enabled(self, client, app):
        """Test pricing page when Stripe is enabled"""
        # Enable Stripe temporarily
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        from app.services.stripe_service import stripe_service
        stripe_service.init_app(app)

        response = client.get('/pricing/')

        assert response.status_code == 200
        assert b'Choose Your Plan' in response.data
        assert b'Basic' in response.data
        assert b'Pro' in response.data
        assert b'Enterprise' in response.data

    def test_pricing_page_shows_mock_warning(self, client, app):
        """Test that pricing page shows warning in mock mode"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        from app.services.stripe_service import stripe_service
        stripe_service.init_app(app)

        response = client.get('/pricing/')

        assert b'Demo Mode' in response.data or b'mock mode' in response.data


class TestCheckoutFlow:
    """Test the checkout flow"""

    def test_create_session_requires_auth(self, client, app):
        """Test that creating checkout session requires authentication"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        response = client.post('/checkout/create-session', data={
            'price_id': 'price_test_basic'
        })

        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.location

    def test_create_session_requires_price_id(self, client, app, logged_in_user):
        """Test that creating checkout session requires price_id"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        response = client.post('/checkout/create-session', data={})

        assert response.status_code == 302
        assert '/pricing' in response.location

    def test_create_session_success(self, client, app, logged_in_user):
        """Test successful checkout session creation"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        from app.services.stripe_service import stripe_service
        stripe_service.init_app(app)

        response = client.post('/checkout/create-session', data={
            'price_id': 'price_test_basic_monthly'
        }, follow_redirects=False)

        # Should redirect to Stripe Checkout (or mock URL)
        assert response.status_code == 302
        assert 'checkout.stripe.com' in response.location or 'mock' in response.location

    def test_checkout_success_page(self, client):
        """Test checkout success page"""
        response = client.get('/checkout/success?session_id=cs_test_12345')

        assert response.status_code == 200
        assert b'Payment Successful' in response.data

    def test_checkout_cancel_page(self, client):
        """Test checkout cancel page"""
        response = client.get('/checkout/cancel')

        assert response.status_code == 200
        assert b'Payment Cancelled' in response.data


class TestWebhookHandler:
    """Test Stripe webhook handling"""

    def test_webhook_rejects_get_requests(self, client, app):
        """Test that webhook only accepts POST requests"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        response = client.get('/webhooks/stripe')

        assert response.status_code == 405
        data = json.loads(response.data)
        assert 'error' in data

    def test_webhook_disabled_when_stripe_off(self, client):
        """Test webhook returns error when Stripe is disabled"""
        response = client.post('/webhooks/stripe', data='{}')

        assert response.status_code == 400

    def test_webhook_checkout_completed(self, client, app, stripe_webhook_event_checkout_completed, db_session):
        """Test webhook handling for checkout.session.completed"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        from app.services.stripe_service import stripe_service
        stripe_service.init_app(app)

        # Create a user with the email from the event
        from app.models import User
        user = User.create_user(
            email=stripe_webhook_event_checkout_completed['data']['object']['customer_email'],
            password='testpass'
        )

        # Send webhook
        payload = json.dumps(stripe_webhook_event_checkout_completed).encode('utf-8')
        response = client.post(
            '/webhooks/stripe',
            data=payload,
            headers={'Stripe-Signature': 'mock_sig'},
            content_type='application/json'
        )

        assert response.status_code == 200

        # Check that user was updated
        with db_session:
            updated_user = User.query.filter_by(email=user.email).first()
            assert updated_user.subscription_status == 'active'
            assert updated_user.stripe_subscription_id is not None

    def test_webhook_subscription_deleted(self, client, app, stripe_webhook_event_subscription_deleted, db_session):
        """Test webhook handling for customer.subscription.deleted"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        from app.services.stripe_service import stripe_service
        stripe_service.init_app(app)

        # Create a user with existing subscription
        from app.models import User
        subscription_id = stripe_webhook_event_subscription_deleted['data']['object']['id']

        user = User.create_user(email='canceled@example.com', password='testpass')
        user.stripe_subscription_id = subscription_id
        user.subscription_status = 'active'
        user.save()

        # Send webhook
        payload = json.dumps(stripe_webhook_event_subscription_deleted).encode('utf-8')
        response = client.post(
            '/webhooks/stripe',
            data=payload,
            headers={'Stripe-Signature': 'mock_sig'},
            content_type='application/json'
        )

        assert response.status_code == 200

        # Check that subscription was canceled
        with db_session:
            updated_user = User.query.filter_by(email=user.email).first()
            assert updated_user.subscription_status == 'canceled'


class TestStripeIntegration:
    """End-to-end integration tests"""

    def test_full_subscription_flow_mock(self, client, app, db_session):
        """Test complete subscription flow in mock mode"""
        # Setup
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'mock'

        from app.services.stripe_service import stripe_service
        stripe_service.init_app(app)

        from app.models import User

        # 1. User signs up
        user = User.create_user(email='flow@example.com', password='testpass')

        # 2. User views pricing page
        # (login user)
        client.post('/login', data={'email': user.email, 'password': 'testpass'})

        response = client.get('/pricing/')
        assert response.status_code == 200

        # 3. User starts checkout
        response = client.post('/checkout/create-session', data={
            'price_id': 'price_test_pro_monthly'
        }, follow_redirects=False)

        assert response.status_code == 302

        # 4. Simulate webhook (subscription activated)
        session = {
            'id': 'cs_test_completed',
            'customer_email': user.email,
            'customer': 'cus_test_123',
            'subscription': 'sub_test_123',
        }

        event = {
            'type': 'checkout.session.completed',
            'data': {'object': session}
        }

        payload = json.dumps(event).encode('utf-8')
        response = client.post(
            '/webhooks/stripe',
            data=payload,
            headers={'Stripe-Signature': 'mock'},
            content_type='application/json'
        )

        assert response.status_code == 200

        # 5. Verify user has active subscription
        with db_session:
            updated_user = User.query.filter_by(email=user.email).first()
            assert updated_user.subscription_status == 'active'
            assert updated_user.stripe_customer_id == 'cus_test_123'
            assert updated_user.stripe_subscription_id == 'sub_test_123'


@pytest.mark.skipif(
    True,  # Always skip unless manually enabled
    reason="Requires real Stripe test keys - enable manually for integration testing"
)
class TestStripeTestMode:
    """
    Tests for Stripe TEST mode (real API calls with test keys).

    To run these tests:
    1. Set environment variables:
       export STRIPE_PUBLISHABLE_KEY=pk_test_...
       export STRIPE_SECRET_KEY=sk_test_...
       export STRIPE_WEBHOOK_SECRET=whsec_test_...
    2. Remove @pytest.mark.skipif decorator
    3. Run: pytest tests/test_stripe.py::TestStripeTestMode -v
    """

    def test_real_stripe_checkout_session(self, app):
        """Test creating real Stripe checkout session with test keys"""
        app.config['stripe_enabled'] = True
        app.config['stripe_mode'] = 'test'
        # Keys should come from environment variables

        service = StripeService(app)

        session = service.create_checkout_session(
            customer_email='test@example.com',
            price_id='price_...',  # Use your actual test price ID
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )

        assert session['id'].startswith('cs_test_')
        assert 'url' in session


# Marker for live mode tests (should NEVER be run automatically)
@pytest.mark.skipif(
    True,
    reason="LIVE MODE TESTS - Never run automatically! Only for manual verification."
)
class TestStripeLiveMode:
    """
    Placeholder for live mode tests.

    These should NEVER be run in CI/CD or automated testing.
    Only use for manual verification with extreme caution.
    """

    def test_live_mode_requires_explicit_confirmation(self):
        """
        Live mode should require explicit confirmation.
        This test is here as a reminder to be extremely careful.
        """
        pytest.fail(
            "Live mode tests should never run automatically. "
            "If you really need to test live mode, do it manually "
            "with a staging/test Stripe account."
        )
