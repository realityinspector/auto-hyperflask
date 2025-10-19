from hyperflask.factory import db
from hyperflask_users import UserMixin, UserRelatedMixin
from sqlalchemy import Index
import datetime


class User(UserMixin, db.Model):
    is_admin: bool = db.Column(default=False)

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

    __table_args__ = (
        Index('ix_timelineentry_timestamp', 'timestamp'),
        Index('ix_timelineentry_user_timestamp', 'user_id', 'timestamp'),
    )
