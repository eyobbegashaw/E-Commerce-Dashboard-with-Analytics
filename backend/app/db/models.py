from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analysis_jobs = relationship("AnalysisJob", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    alert_configs = relationship("AlertConfig", back_populates="user", cascade="all, delete-orphan")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_name = Column(String(200))
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    total_comments = Column(Integer, default=0)
    processed_comments = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="analysis_jobs")
    comments = relationship("Comment", back_populates="job", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    original_text = Column(Text, nullable=False)
    sentiment = Column(String(10), nullable=False)  # positive, negative, neutral
    confidence = Column(Float)
    keywords = Column(ARRAY(String), default=[])
    source = Column(String(50))  # facebook, telegram, youtube, manual, csv
    metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("AnalysisJob", back_populates="comments")
    user = relationship("User", back_populates="comments")

class AlertConfig(Base):
    __tablename__ = "alert_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    email_enabled = Column(Boolean, default=False)
    sms_enabled = Column(Boolean, default=False)
    threshold = Column(Float, default=0.3)
    time_window = Column(Integer, default=30)  # minutes
    notification_emails = Column(ARRAY(String), default=[])
    phone_numbers = Column(ARRAY(String), default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alert_configs")

class SentimentDaily(Base):
    __tablename__ = "sentiment_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    job_id = Column(Integer, ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=True)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Indexes for performance
from sqlalchemy import Index
Index('idx_comments_sentiment', Comment.sentiment)
Index('idx_comments_created_at', Comment.created_at)
Index('idx_comments_job_id', Comment.job_id)
Index('idx_jobs_user_id', AnalysisJob.user_id)
Index('idx_jobs_status', AnalysisJob.status)