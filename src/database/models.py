from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    level = Column(String)
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    achievements = relationship("Achievement", back_populates="user")
    statistics = relationship("Statistics", back_populates="user")

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    date_earned = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="achievements")

class Statistics(Base):
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    messages_count = Column(Integer, default=0)
    corrections_count = Column(Integer, default=0)
    exercises_completed = Column(Integer, default=0)
    user = relationship("User", back_populates="statistics") 