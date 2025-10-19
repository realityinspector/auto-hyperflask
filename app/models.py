from hyperflask.factory import db
from hyperflask_users import UserMixin, UserRelatedMixin
from sqlalchemy import Index
import datetime


class User(UserMixin, db.Model):
    is_admin: bool = db.Column(default=False)

    # Stripe subscription fields (optional - only used if Stripe is enabled)
    stripe_customer_id: str = db.Column(nullable=True, unique=True)
    stripe_subscription_id: str = db.Column(nullable=True)
    subscription_status: str = db.Column(nullable=True)  # active, canceled, past_due, trialing
    subscription_plan: str = db.Column(nullable=True)    # basic, pro, enterprise (or your plan names)
    subscription_ends_at: datetime.datetime = db.Column(nullable=True)

    @classmethod
    def create_user(cls, email, password=None, **kwargs):
        """
        Create a new user. First registered user becomes admin automatically.
        """
        # Check if this is the first user
        with db:
            user_count = cls.count()
            is_first_user = user_count == 0

            # Create user with admin flag if first user
            user = cls.create(
                email=email,
                is_admin=is_first_user,
                **kwargs
            )

            # Set password if provided
            if password:
                user.set_password(password)
                user.save()

            if is_first_user:
                print(f"✨ First user registered: {email} (granted admin privileges)")

            return user


class TimelineEntry(UserRelatedMixin, db.Model):
    timestamp: datetime.datetime
    status: str = db.Column(default='pending')
    created_at: datetime.datetime = db.Column(default=datetime.datetime.utcnow)
    photo_url: str = db.Column(nullable=True)
    caption: str = db.Column(nullable=True)

    # Optional: Link timeline entry to a product
    product_id: int = db.Column(db.ForeignKey('product.id'), nullable=True)

    __table_args__ = (
        Index('ix_timelineentry_timestamp', 'timestamp'),
        Index('ix_timelineentry_user_timestamp', 'user_id', 'timestamp'),
    )


class Product(db.Model):
    """
    Product model for e-commerce functionality.
    Integrates with timeline (users can post about products) and subscriptions.
    """
    id: int
    name: str = db.Column(nullable=False)
    description: str = db.Column(nullable=True)
    price: int = db.Column(nullable=False)  # Price in cents
    image_url: str = db.Column(nullable=True)
    category: str = db.Column(nullable=True)
    is_active: bool = db.Column(default=True)
    stock_quantity: int = db.Column(default=0)

    # Subscription gating: require certain subscription tier to purchase
    requires_subscription: str = db.Column(nullable=True)  # 'basic', 'pro', 'enterprise', or null

    created_at: datetime.datetime = db.Column(default=datetime.datetime.utcnow)
    updated_at: datetime.datetime = db.Column(default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relations
    created_by_id: int = db.Column(db.ForeignKey('user.id'), nullable=True)

    __table_args__ = (
        Index('ix_product_category', 'category'),
        Index('ix_product_is_active', 'is_active'),
    )


class CartItem(db.Model):
    """Shopping cart items"""
    id: int
    user_id: int = db.Column(db.ForeignKey('user.id'), nullable=False)
    product_id: int = db.Column(db.ForeignKey('product.id'), nullable=False)
    quantity: int = db.Column(default=1)
    added_at: datetime.datetime = db.Column(default=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_cartitem_user', 'user_id'),
        Index('ix_cartitem_product', 'product_id'),
    )


class Order(UserRelatedMixin, db.Model):
    """
    Order model for completed purchases.
    Linked to Stripe payment intents.
    """
    id: int
    order_number: str = db.Column(nullable=False, unique=True)
    status: str = db.Column(default='pending')  # pending, paid, shipped, completed, canceled
    total_amount: int = db.Column(nullable=False)  # Total in cents

    # Stripe integration
    stripe_payment_intent_id: str = db.Column(nullable=True)
    stripe_payment_status: str = db.Column(nullable=True)

    # Shipping info
    shipping_name: str = db.Column(nullable=True)
    shipping_address: str = db.Column(nullable=True)
    shipping_city: str = db.Column(nullable=True)
    shipping_postal_code: str = db.Column(nullable=True)
    shipping_country: str = db.Column(nullable=True)

    created_at: datetime.datetime = db.Column(default=datetime.datetime.utcnow)
    updated_at: datetime.datetime = db.Column(default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        Index('ix_order_user', 'user_id'),
        Index('ix_order_status', 'status'),
        Index('ix_order_number', 'order_number'),
    )


class OrderItem(db.Model):
    """Items within an order"""
    id: int
    order_id: int = db.Column(db.ForeignKey('order.id'), nullable=False)
    product_id: int = db.Column(db.ForeignKey('product.id'), nullable=False)
    quantity: int = db.Column(nullable=False)
    price_at_purchase: int = db.Column(nullable=False)  # Price in cents at time of purchase
    product_name: str = db.Column(nullable=False)  # Snapshot of product name

    __table_args__ = (
        Index('ix_orderitem_order', 'order_id'),
        Index('ix_orderitem_product', 'product_id'),
    )
