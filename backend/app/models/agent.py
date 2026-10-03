"""SQLAlchemy Model for Agent Identity and Permissions."""

from sqlalchemy import Column, String, Text, Boolean, JSON
from app.database import Base


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String(64), primary_key=True, index=True)  # e.g., "FIN-001"
    name = Column(String(128), nullable=False)               # "Finance Analyst Agent"
    department = Column(String(64), nullable=False)         # "Finance"
    purpose = Column(Text, nullable=False)                  # Declared purpose
    allowed_resources = Column(JSON, default=list)          # ["finance_db", "invoice_api", ...]
    restricted_resources = Column(JSON, default=list)       # ["hr_db", "customer_pii", ...]
    external_access = Column(String(32), default="restricted") # "blocked", "restricted", "allowed"
    base_risk_level = Column(String(16), default="MEDIUM")  # "LOW", "MEDIUM", "HIGH"
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "purpose": self.purpose,
            "allowed_resources": self.allowed_resources or [],
            "restricted_resources": self.restricted_resources or [],
            "external_access": self.external_access,
            "base_risk_level": self.base_risk_level,
            "is_active": self.is_active,
        }
