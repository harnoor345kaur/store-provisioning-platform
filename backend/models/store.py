from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)

    store_id = Column(String, unique=True, index=True)
    namespace = Column(String)

    status = Column(String)

    nodeport_url = Column(String)
    ingress_url = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Observability fields
    provision_duration = Column(Integer)
    failure_reason = Column(Text)
    event_logs = Column(Text)
