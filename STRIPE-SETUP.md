# Stripe Integration Setup Guide

> **Optional Stripe subscriptions for AutoHyperFlask with mock/test/live modes**

AutoHyperFlask includes optional Stripe subscription support with three modes:
- **Mock** (default): Works out of the box, no Stripe account needed
- **Test**: Uses Stripe test mode for realistic testing
- **Live**: Production-ready with real payments

## 🚀 Quick Start (Mock Mode)

Stripe integration is **disabled by default**. To enable it in mock mode:

1. **Update your config:**
   ```yaml
   # config_dev.yml
   stripe_enabled: true
   stripe_mode: mock
   ```

2. **Install Stripe dependencies** (optional):
   ```bash
   pip install -e ".[stripe]"
   ```

3. **Reset database** to add subscription fields:
   ```bash
   python3 scripts/reset_db.py --seed --confirm
   ```

4. **Visit** http://localhost:5000/pricing

That's it! Mock mode simulates the entire Stripe flow without any API calls.

---

## 📚 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Mode Comparison](#mode-comparison)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Mock Mode (Development)](#mock-mode-development)
- [Test Mode (Staging)](#test-mode-staging)
- [Live Mode (Production)](#live-mode-production)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

---

## Architecture Overview

The Stripe integration consists of:

### Files Structure
```
app/
├── models.py                    # User model with subscription fields
├── services/
│   └── stripe_service.py        # StripeService (mock/test/live)
└── pages/
    ├── pricing/
    │   └── index.jpy            # Pricing page
    ├── checkout/
    │   ├── create-session.jpy   # Create Checkout session
    │   ├── success.jpy          # Payment success page
    │   └── cancel.jpy           # Payment cancelled page
    └── webhooks/
        └── stripe.jpy           # Webhook handler

tests/
├── fixtures/
│   └── stripe_fixtures.py       # Pytest fixtures for Stripe
└── test_stripe.py               # Comprehensive Stripe tests
```

### Service Layer

`StripeService` provides a unified API across all modes:

```python
from app.services.stripe_service import stripe_service

# Create checkout session (works in all modes)
session = stripe_service.create_checkout_session(
    customer_email=user.email,
    price_id='price_...',
    success_url='...',
    cancel_url='...'
)

# Handle webhooks (works in all modes)
event = stripe_service.construct_webhook_event(payload, signature)
```

---

## Mode Comparison

| Feature | Mock Mode | Test Mode | Live Mode |
|---------|-----------|-----------|-----------|
| **Stripe Account Required** | ❌ No | ✅ Yes (free) | ✅ Yes |
| **API Calls** | None | Real (test keys) | Real (live keys) |
| **Real Payments** | ❌ No | ❌ No | ✅ Yes |
| **Webhook Testing** | ✅ Easy | ⚠️ Needs CLI/tunneling | ⚠️ Needs HTTPS |
| **Development Speed** | ⚡ Instant | 🐢 API latency | 🐢 API latency |
| **Best For** | Development | Staging | Production |

**Recommendation:** Use Mock mode for development, Test mode for staging, Live mode only in production.

---

## Configuration

### Development (`config_dev.yml`)

```yaml
# Stripe configuration
stripe_enabled: false  # Toggle to true to enable
stripe_mode: mock      # mock, test, or live
stripe_publishable_key: ${STRIPE_PUBLISHABLE_KEY:-pk_test_mock}
stripe_secret_key: ${STRIPE_SECRET_KEY:-sk_test_mock}
stripe_webhook_secret: ${STRIPE_WEBHOOK_SECRET:-whsec_mock}
```

### Production (`config_prod.yml`)

```yaml
# Stripe configuration
stripe_enabled: ${STRIPE_ENABLED:-false}
stripe_mode: ${STRIPE_MODE:-test}
stripe_publishable_key: ${STRIPE_PUBLISHABLE_KEY}
stripe_secret_key: ${STRIPE_SECRET_KEY}
stripe_webhook_secret: ${STRIPE_WEBHOOK_SECRET}
```

### Environment Variables

```bash
# Test mode
export STRIPE_ENABLED=true
export STRIPE_MODE=test
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_test_...

# Live mode (production only!)
export STRIPE_ENABLED=true
export STRIPE_MODE=live
export STRIPE_PUBLISHABLE_KEY=pk_live_...
export STRIPE_SECRET_KEY=sk_live_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

**On Replit:**
Set these in **Tools → Secrets** (not environment variables).

---

## Database Schema

The User model is extended with subscription fields:

```python
class User(UserMixin, db.Model):
    # ... existing fields ...

    # Stripe subscription fields
    stripe_customer_id: str             # Stripe customer ID (cus_...)
    stripe_subscription_id: str         # Stripe subscription ID (sub_...)
    subscription_status: str            # active, canceled, past_due, trialing
    subscription_plan: str              # basic, pro, enterprise (your plan names)
    subscription_ends_at: datetime      # Subscription renewal/end date
```

**Migration:**
After enabling Stripe, reset your database:
```bash
python3 scripts/reset_db.py --seed --confirm
```

Or if you have existing data, create a migration (when Alembic is set up).

---

## Mock Mode (Development)

### Enable Mock Mode

```yaml
# config_dev.yml
stripe_enabled: true
stripe_mode: mock
```

### How It Works

Mock mode simulates Stripe's API without making real HTTP requests:

1. **Checkout Sessions**: Returns mock `cs_test_...` IDs with fake URLs
2. **Webhooks**: Accepts any payload, no signature verification
3. **Subscriptions**: Stored in memory, reset on restart
4. **Customer IDs**: Generated as `cus_mock_...`

### Testing Checkout Flow

```python
# In tests or manual testing
from app.services.stripe_service import StripeService

service = StripeService(app)

# Create session
session = service.create_checkout_session(
    customer_email='test@example.com',
    price_id='price_test_basic',
    success_url='...',
    cancel_url='...'
)

# Simulate payment completion (only works in mock mode)
completed = service._complete_mock_checkout(session['id'])

# completed_session now has customer_id and subscription_id
```

### Simulating Webhooks

```bash
curl -X POST http://localhost:5000/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{
    "type": "checkout.session.completed",
    "data": {
      "object": {
        "id": "cs_test_mock",
        "customer_email": "user1@test.com",
        "customer": "cus_mock_123",
        "subscription": "sub_mock_456"
      }
    }
  }'
```

---

## Test Mode (Staging)

### 1. Create Stripe Test Account

1. Sign up at https://stripe.com (free)
2. Navigate to **Developers** → **API keys**
3. Toggle **Viewing test data** (top right)

### 2. Get Test API Keys

Copy your test keys:
- **Publishable key**: `pk_test_...`
- **Secret key**: `sk_test_...`

### 3. Create Products and Prices

1. Go to **Products** → **Add product**
2. Create products (e.g., "Basic Plan", "Pro Plan")
3. Add prices (e.g., $9.00/month)
4. Copy the **Price ID** (e.g., `price_1ABC...`)

### 4. Update Pricing Page

Edit `app/pages/pricing/index.jpy`:

```python
plans = [
    {
        'name': 'Basic',
        'price': '$9',
        'period': 'month',
        'price_id': 'price_1ABC...',  # Your actual test Price ID
        # ...
    },
]
```

### 5. Configure Webhooks

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login: `stripe login`
3. Forward webhooks to local:
   ```bash
   stripe listen --forward-to localhost:5000/webhooks/stripe
   ```
4. Copy the webhook signing secret: `whsec_...`

### 6. Set Environment Variables

```bash
export STRIPE_ENABLED=true
export STRIPE_MODE=test
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

### 7. Test Checkout

1. Visit http://localhost:5000/pricing
2. Click a plan
3. Use test card: `4242 4242 4242 4242`
4. Expiry: Any future date
5. CVC: Any 3 digits

---

## Live Mode (Production)

### ⚠️ Production Checklist

Before enabling live mode:

- [ ] Verified test mode works perfectly
- [ ] All webhooks handle errors gracefully
- [ ] Subscription status checks in place
- [ ] Configured proper plan names and Price IDs
- [ ] Set up proper error monitoring
- [ ] Tested subscription cancellation flow
- [ ] Configured HTTPS (required for live webhooks)
- [ ] Reviewed Stripe security best practices

### 1. Get Live API Keys

1. In Stripe Dashboard, toggle **Viewing live data**
2. Go to **Developers** → **API keys**
3. Copy live keys: `pk_live_...` and `sk_live_...`

⚠️ **Never commit live keys to git!**

### 2. Create Live Products

Create the same products/prices in live mode as you tested.

### 3. Configure Live Webhooks

1. Go to **Developers** → **Webhooks**
2. Add endpoint: `https://your-domain.com/webhooks/stripe`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook signing secret: `whsec_...`

### 4. Set Production Environment Variables

**On Replit** (Tools → Secrets):
```
STRIPE_ENABLED=true
STRIPE_MODE=live
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 5. Test with Real Card

Use a **small amount** first (e.g., create a $1 test plan) to verify everything works.

---

## Testing

### Run Stripe Tests

```bash
# All Stripe tests (mock mode)
pytest tests/test_stripe.py -v

# Specific test class
pytest tests/test_stripe.py::TestMockStripeAPI -v

# With coverage
pytest tests/test_stripe.py -v --cov=app.services.stripe_service
```

### Test Fixtures Available

```python
# In your tests
def test_my_feature(stripe_service_mock, mock_checkout_session):
    # stripe_service_mock: StripeService in mock mode
    # mock_checkout_session: Pre-created checkout session
    ...
```

See `tests/fixtures/stripe_fixtures.py` for all available fixtures.

### Manual Testing Checklist

- [ ] Visit /pricing (should show plans)
- [ ] Click plan (redirects to checkout)
- [ ] Complete checkout (test card in test mode)
- [ ] Visit /checkout/success
- [ ] Check user subscription status updated
- [ ] Cancel subscription
- [ ] Verify webhook processing

---

## Troubleshooting

### "Stripe is not enabled"

**Cause:** `stripe_enabled: false` in config

**Fix:**
```yaml
stripe_enabled: true
```

### "Stripe SDK not installed"

**Cause:** Optional Stripe dependencies not installed

**Fix:**
```bash
pip install -e ".[stripe]"
```

### "Invalid webhook signature"

**Cause:** Wrong `STRIPE_WEBHOOK_SECRET` or signature verification issue

**Fix (Test Mode):**
- Use Stripe CLI: `stripe listen --forward-to localhost:5000/webhooks/stripe`
- Copy the new webhook secret

**Fix (Live Mode):**
- Verify webhook secret from Stripe Dashboard matches environment variable

### Webhooks not received

**Mock Mode:**
- Webhooks must be sent manually (curl or test code)

**Test Mode:**
- Ensure Stripe CLI is running: `stripe listen`
- Check Stripe CLI output for errors

**Live Mode:**
- Verify endpoint is HTTPS
- Check Stripe Dashboard → Webhooks → Event Logs for delivery errors

### Subscription not activating

**Check:**
1. Webhook handler is working (check logs)
2. User email matches checkout session email
3. Database has subscription fields
4. No errors in webhook processing

**Debug:**
```python
# Add logging to app/pages/webhooks/stripe.jpy
print(f"Webhook received: {event_type}")
print(f"Event data: {event_data}")
```

---

## Security

### Never Commit Secrets

❌ **Bad:**
```yaml
stripe_secret_key: sk_live_12345...
```

✅ **Good:**
```yaml
stripe_secret_key: ${STRIPE_SECRET_KEY}
```

### Verify Webhook Signatures

The webhook handler automatically verifies signatures in test/live mode:

```python
# In stripe_service.py
event = stripe.Webhook.construct_event(
    payload, sig_header, webhook_secret
)  # Raises error if invalid
```

### Restrict API Keys

In Stripe Dashboard:
- **Developers** → **API keys** → **Restricted keys**
- Create restricted keys with minimal permissions:
  - `checkout_sessions:write`
  - `customers:read`
  - `subscriptions:read`

### Monitor Webhook Failures

- Set up error monitoring (Sentry, etc.)
- Review Stripe Dashboard → **Webhooks** → **Event Logs**
- Handle failed payments gracefully

---

## Toggle On/Off

### Disable Stripe Completely

```yaml
# config.yml
stripe_enabled: false
```

All Stripe pages will redirect to home with a message.

### Enable for Specific Users (Future Enhancement)

```python
# In app/pages/pricing/index.jpy
if not current_user.is_admin:
    page.redirect = '/'
    return
```

### Feature Gating Based on Subscription

```python
# Example: Limit timeline entries
from app.services.stripe_service import stripe_service

if stripe_service.is_enabled():
    if not current_user.subscription_status == 'active':
        page.flash('Upgrade to add more entries', 'warning')
        page.redirect = '/pricing'
        return
```

---

## Next Steps

1. **Customize Plans**: Edit `app/pages/pricing/index.jpy` with your pricing
2. **Add Features**: Implement subscription-gated features
3. **Test Thoroughly**: Run full test suite
4. **Monitor**: Set up Stripe Dashboard notifications
5. **Iterate**: Adjust plans based on user feedback

---

## Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Testing**: https://stripe.com/docs/testing
- **Stripe CLI**: https://stripe.com/docs/stripe-cli
- **Webhook Testing**: https://stripe.com/docs/webhooks/test

---

## Support

- **AutoHyperFlask Issues**: https://github.com/realityinspector/auto-hyperflask/issues
- **Stripe Support**: https://support.stripe.com
- **Hyperflask Discord**: https://discord.gg/hyperflask (ask in #help)

---

**Happy building! 🚀**
