from sqlalchemy import String, JSON, TIMESTAMP
from sqlalchemy.schema import (
    Column,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class ShopSession(Base):
    __tablename__ = "shop_sessions"
    # @NOTE: This is a STRING primary key.
    id = Column(String(255), primary_key=True)
    value = Column(JSON, nullable=False)
    shop_name = Column(String(255))
    type = Column(String(50))
    created_on = Column(TIMESTAMP)
    modified_on = Column(TIMESTAMP)
