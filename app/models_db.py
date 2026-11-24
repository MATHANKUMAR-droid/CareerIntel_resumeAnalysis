from sqlalchemy import String,Text,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime,timezone
from app.db import Base
class StoredResume(Base):
 __tablename__='resumes';id:Mapped[str]=mapped_column(String,primary_key=True);profile_json:Mapped[str]=mapped_column(Text);source_text:Mapped[str]=mapped_column(Text)
class StoredJob(Base):
 __tablename__='jobs';id:Mapped[str]=mapped_column(String,primary_key=True);job_json:Mapped[str]=mapped_column(Text)
class StoredMatch(Base):
 __tablename__='matches';id:Mapped[str]=mapped_column(String,primary_key=True);assessment_json:Mapped[str]=mapped_column(Text)
class CareerEvidence(Base):
 __tablename__='career_evidence';id:Mapped[str]=mapped_column(String,primary_key=True);resume_id:Mapped[str]=mapped_column(ForeignKey('resumes.id'));requirement_id:Mapped[str]=mapped_column(String);answer:Mapped[str]=mapped_column(Text);status:Mapped[str]=mapped_column(String,default='pending');source:Mapped[str]=mapped_column(String,default='user_clarification');created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
