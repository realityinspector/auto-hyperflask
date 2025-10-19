"""
Pytest fixtures for Stripe testing.

These fixtures provide mock Stripe functionality for tests without requiring
real Stripe API calls or credentials.

Usage:
    def test_checkout(stripe_service, mock_stripe_customer):
        # stripe_service is in mock mode
        # mock_stripe_customer is a pre-created customer
        ...
"""
import pytest
from app.services.stripe_service import StripeService, MockStripeAPI


@pytest.fixture
def mock_stripe_api():
    """Provide a fresh MockStripeAPI instance for testing"""
    return MockStripeAPI()


@pytest.fixture
def stripe_service_mock(app):
    """
    Provide a StripeService in mock mode.
    This is the primary fixture for testing Stripe functionality.
    """
    # Temporarily enable Stripe and set to mock mode
    original_enabled = app.config.get('stripe_enabled')
    original_mode = app.config.get('stripe_mode')

    app.config['stripe_enabled'] = True
    app.config['stripe_mode'] = 'mock'
    app.config['stripe_publishable_key'] = 'pk_test_mock'
    app.config['stripe_secret_key'] = 'sk_test_mock'
    app.config['stripe_webhook_secret'] = 'whsec_mock'

    service = StripeService(app)

    yield service

    # Restore original config
    app.config['stripe_enabled'] = original_enabled
    app.config['stripe_mode'] = original_mode


@pytest.fixture
def mock_stripe_customer(stripe_service_mock):
    """Create a mock Stripe customer for testing"""
    customer = stripe_service_mock._get_mock_api().create_customer(
        email='test@example.com',
        metadata={'test': 'true'}
    )
    return customer


@pytest.fixture
def mock_stripe_subscription(stripe_service_mock, mock_stripe_customer):
    """Create a mock Stripe subscription for testing"""
    subscription = stripe_service_mock._get_mock_api().create_subscription(
        customer_id=mock_stripe_customer['id'],
        price_id='price_test_basic_monthly',
        metadata={'plan': 'basic'}
    )
    return subscription


@pytest.fixture
def mock_checkout_session(stripe_service_mock):
    """Create a mock checkout session for testing"""
    session = stripe_service_mock.create_checkout_session(
        customer_email='test@example.com',
        price_id='price_test_basic_monthly',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
        mode='subscription'
    )
    return session


@pytest.fixture
def completed_checkout_session(stripe_service_mock, mock_checkout_session):
    """
    Create a completed checkout session (simulating successful payment).
    Useful for testing webhook handlers.
    """
    session = stripe_service_mock._complete_mock_checkout(mock_checkout_session['id'])
    return session


@pytest.fixture
def stripe_webhook_event_checkout_completed(completed_checkout_session):
    """
    Create a mock webhook event for checkout.session.completed.
    This is what Stripe sends when a customer completes payment.
    """
    return {
        'id': 'evt_test_webhook_checkout_completed',
        'object': 'event',
        'type': 'checkout.session.completed',
        'data': {
            'object': completed_checkout_session
        }
    }


@pytest.fixture
def stripe_webhook_event_subscription_deleted(mock_stripe_subscription):
    """
    Create a mock webhook event for customer.subscription.deleted.
    This is what Stripe sends when a subscription is canceled.
    """
    # Mark subscription as canceled
    mock_stripe_subscription['status'] = 'canceled'

    return {
        'id': 'evt_test_webhook_subscription_deleted',
        'object': 'event',
        'type': 'customer.subscription.deleted',
        'data': {
            'object': mock_stripe_subscription
        }
    }


@pytest.fixture
def stripe_webhook_payload(stripe_webhook_event_checkout_completed):
    """
    Create a webhook payload (JSON bytes) for testing webhook endpoints.
    """
    import json
    return json.dumps(stripe_webhook_event_checkout_completed).encode('utf-8')


@pytest.fixture
def stripe_plans():
    """
    Sample Stripe plans for testing pricing pages.
    These would correspond to actual Stripe Price IDs in production.
    """
    return [
        {
            'name': 'Basic',
            'price': '$9/month',
            'price_amount': 900,  # cents
            'price_id': 'price_test_basic_monthly',
            'features': ['Feature 1', 'Feature 2', 'Feature 3']
        },
        {
            'name': 'Pro',
            'price': '$29/month',
            'price_amount': 2900,
            'price_id': 'price_test_pro_monthly',
            'features': ['Everything in Basic', 'Feature 4', 'Feature 5', 'Priority support']
        },
        {
            'name': 'Enterprise',
            'price': '$99/month',
            'price_amount': 9900,
            'price_id': 'price_test_enterprise_monthly',
            'features': ['Everything in Pro', 'Feature 6', 'Custom integrations', 'Dedicated support']
        }
    ]
