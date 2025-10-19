# Content + Commerce Integration

> **How AutoHyperFlask combines Timeline (content) and Shop (commerce) into one unified platform**

Auto Hyperflask is a **hybrid content + commerce platform** - like WordPress and Shopify combined. Users can create timeline content AND browse/purchase products, with deep integration between both features.

## 🎯 The Vision

Think of it as **social commerce**: users share their experiences with products on a timeline while also being able to purchase those products directly.

- **Content creators** post about their favorite products
- **Shoppers** discover products through authentic user posts
- **Community** forms around shared interests and products
- **Monetization** through product sales and subscriptions

## 📊 Architecture

### Database Integration

```
User ─┬─ TimelineEntry ──┐
      │                  │
      ├─ CartItem        │ (optional link)
      │                  │
      ├─ Order           │
      │                  ▼
      └─ Subscription   Product
```

**Key relationships:**
- `TimelineEntry.product_id` → links posts to products (optional)
- `User.subscription_status` → gates features in both timeline and shop
- Products can have `requires_subscription` → only subscribers can buy

### URL Structure

```
/                           Homepage (shows both features)
├── /timeline               Content features
│   ├── /timeline           Browse all posts
│   ├── /timeline/new       Create new post
│   └── /timeline?product_id=X  Posts about a specific product
│
├── /shop                   Commerce features
│   ├── /shop               Product catalog
│   ├── /shop/product/X     Product details + related timeline posts
│   ├── /shop/cart          Shopping cart
│   └── /shop/orders        Order history
│
├── /pricing                Subscriptions (gates both features)
└── /admin                  Manage both content and products
```

## 🔗 Integration Points

### 1. Timeline Posts About Products

**Use case:** User loves a product and posts about it

```python
# app/pages/timeline/new.jpy
# User can optionally link their post to a product

TimelineEntry.create(
    user_id=current_user.id,
    caption="Just got this amazing camera!",
    photo_url="/photos/camera.jpg",
    product_id=42  # Links to product
)
```

**Result:**
- Post appears on timeline with product tag
- Post appears on product page under "Community Posts"
- Social proof for products

### 2. Product Pages Show User Content

**Use case:** Shopper wants to see real user experiences

```python
# app/pages/shop/product/[id].jpy
# Product page shows timeline entries mentioning this product

timeline_entries = TimelineEntry.query
    .filter_by(product_id=product_id, status='approved')
    .order_by(TimelineEntry.created_at.desc())
    .all()
```

**Result:**
- Authentic user-generated content on product pages
- Increased trust and conversion
- Community engagement

### 3. Subscription-Gated Features

**Use case:** Premium features require subscription

```python
# Timeline: Limit posts per month for free users
if not user.subscription_status == 'active':
    posts_this_month = count_user_posts_this_month(user)
    if posts_this_month >= 10:
        redirect_to('/pricing')

# Shop: Exclusive products for subscribers
product.requires_subscription = 'pro'
if user.subscription_plan != 'pro':
    show_subscribe_button()
```

**Result:**
- Monetization through subscriptions
- Premium features in both content and commerce
- Clear value proposition

### 4. Cross-Feature Discovery

**Use case:** Users discover new content/products

- **From Timeline → Shop**: See a cool product in someone's post? Click through to buy it
- **From Shop → Timeline**: Like a product? See what others are saying about it
- **Homepage**: Shows featured products AND recent timeline posts side-by-side

## 💡 Business Models Enabled

### 1. Marketplace + Community

```
Users post reviews/experiences → Drive product sales → Platform takes commission
```

**Examples:**
- Fashion community sharing outfits (timeline) + selling clothes (shop)
- Tech reviewers sharing benchmarks (timeline) + hardware store (shop)
- Food bloggers sharing recipes (timeline) + selling ingredients (shop)

### 2. Creator Economy

```
Creators post content → Build audience → Sell merch/products
```

**Examples:**
- Artist shares work process (timeline) + sells prints (shop)
- Fitness coach shares workouts (timeline) + sells programs (shop)
- Photographer shares photos (timeline) + sells presets (shop)

### 3. SaaS + Commerce Hybrid

```
Subscription unlocks premium features → Users get exclusive products
```

**Examples:**
- Basic: 10 timeline posts/month, browse products
- Pro: Unlimited posts, exclusive product access
- Enterprise: Advanced analytics, bulk ordering

## 🛠️ Developer Guide

### Adding Product Links to Timeline Posts

```python
# 1. Add product selector to timeline creation form
# app/pages/timeline/new.jpy

products = Product.query.filter_by(is_active=True).all()
page.products = products

# In template:
<select name="product_id">
    <option value="">No product</option>
    {% for product in products %}
    <option value="{{ product.id }}">{{ product.name }}</option>
    {% endfor %}
</select>
```

### Showing Product-Linked Posts

```python
# app/pages/timeline/index.jpy

entries_with_products = TimelineEntry.query
    .filter(TimelineEntry.product_id.isnot(None))
    .join(Product)
    .all()

for entry in entries_with_products:
    product = Product.query.get(entry.product_id)
    # Show product info alongside post
```

### Subscription Feature Gating

```python
# Helper function to check subscription access
def requires_subscription(tier='basic'):
    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.subscription_status == 'active':
        flash(f'This feature requires a {tier} subscription')
        return redirect('/pricing')

    if tier != 'basic' and current_user.subscription_plan != tier:
        flash(f'Upgrade to {tier} to access this feature')
        return redirect('/pricing')

# Usage in pages:
if requires_subscription('pro'):
    return  # Stops execution, already redirected

# Feature available...
```

## 📈 Example User Flows

### Flow 1: Content-Driven Purchase

1. User browses timeline
2. Sees cool product in someone's post
3. Clicks product tag → product page
4. Sees more user posts about product
5. Adds to cart and purchases
6. Posts their own experience

### Flow 2: Product-Driven Engagement

1. User browses shop
2. Finds interesting product
3. Views community posts tab
4. Sees authentic user reviews
5. Purchases product
6. Becomes active community member

### Flow 3: Subscription Upsell

1. Free user hits timeline post limit
2. Prompted to upgrade to Pro
3. Subscribes for unlimited posts
4. Discovers subscriber-exclusive products
5. Purchases exclusive items
6. Creates more content about them

## 🎨 UI/UX Integration

### Navigation

```html
<nav>
    <a href="/timeline">📅 Timeline</a>
    <a href="/shop">🛍️ Shop</a>
    <a href="/pricing">⭐ Upgrade</a>
</nav>
```

### Homepage

```
Hero: "Content + Commerce Platform"
├── Timeline Section (recent posts)
├── Shop Section (featured products)
└── How They Work Together
```

### Product Pages

```
Product Details
├── Images, price, description
├── Add to Cart button
└── Community Posts Section ← Timeline integration
    └── Real user photos/reviews
```

### Timeline Posts

```
Timeline Entry
├── Photo/caption
├── User info
└── [Tagged Product] ← Shop integration
    └── Inline product preview
```

## 🚀 Deployment Scenarios

### Scenario 1: Content-First Platform

Enable timeline by default, shop is optional:

```yaml
# config.yml
timeline_enabled: true
shop_enabled: false  # Enable later
```

### Scenario 2: Commerce-First Platform

Enable shop by default, timeline is community feature:

```yaml
# config.yml
timeline_enabled: true  # For user reviews
shop_enabled: true
requires_purchase_to_post: true  # Only buyers can post
```

### Scenario 3: Balanced Hybrid (Recommended)

Both features equally important:

```yaml
# config.yml
timeline_enabled: true
shop_enabled: true
allow_product_linking: true
```

## 📝 Customization Ideas

### For Content-Heavy Platforms

- Timeline entries are primary
- Products are "recommended resources"
- Subscription unlocks ad-free timeline + discounts

### For Commerce-Heavy Platforms

- Products are primary
- Timeline is "customer reviews/UGC"
- Subscription unlocks exclusive products

### For Balanced Platforms

- Equal weight to both
- Timeline drives product discovery
- Products fund content creation
- Subscription enhances both

## ✅ Benefits of Integration

**Vs. Separate Timeline App:**
- ✅ Products fund content creation
- ✅ Built-in monetization
- ✅ Social proof for sales
- ✅ Community-driven commerce

**Vs. Separate Shop:**
- ✅ User-generated content
- ✅ Authentic reviews
- ✅ Community engagement
- ✅ Reduced marketing costs

**Combined Benefits:**
- ✅ Network effects (content → sales → content)
- ✅ Multiple revenue streams (products + subscriptions)
- ✅ Engaged community
- ✅ Sustainable business model

---

**This is the power of AutoHyperFlask: Content + Commerce, fully integrated, ready to deploy.**

Fork it. Customize it. Build your hybrid platform.
