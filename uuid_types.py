"""Custom SQLAlchemy type that always returns str, never uuid.UUID"""
import uuid
from sqlalchemy import TypeDecorator, Text

class UUIDText(TypeDecorator):
    """Stores UUIDs as text, always returns str."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)
