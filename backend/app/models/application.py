from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    company = Column(String)
    role = Column(String)
    match_score = Column(Integer)
    priority = Column(String)
    should_apply = Column(String)
    status = Column(String)
    application_date = Column(String)
    job_link = Column(String)
