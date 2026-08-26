from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()

class Cryptocurrency(Base):
    """نموذج العملة الرقمية"""
    __tablename__ = 'cryptocurrencies'
    
    id = Column(String(50), primary_key=True, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    current_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    total_volume = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    price_change_percent_24h = Column(Float, nullable=True)
    price_change_percent_7d = Column(Float, nullable=True)
    circulating_supply = Column(Float, nullable=True)
    total_supply = Column(Float, nullable=True)
    max_supply = Column(Float, nullable=True)
    ath = Column(Float, nullable=True)  # All Time High
    atl = Column(Float, nullable=True)  # All Time Low
    homepage = Column(String(500), nullable=True)
    blockchain_site = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_new = Column(Boolean, default=False, index=True)
    first_seen_date = Column(DateTime, nullable=True, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_price', 'symbol', 'current_price'),
        Index('idx_market_cap_date', 'market_cap', 'last_updated'),
        Index('idx_new_coins', 'is_new', 'first_seen_date'),
    )

class PriceHistory(Base):
    """سجل تاريخ الأسعار"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(50), index=True, nullable=False)
    price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_crypto_timestamp', 'crypto_id', 'timestamp'),
    )

class Alert(Base):
    """التنبيهات"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(50), index=True, nullable=False)
    crypto_name = Column(String(255), nullable=False)
    alert_type = Column(String(50), nullable=False)  # price_increase, volume_increase, new_coin
    alert_message = Column(Text, nullable=False)
    old_value = Column(Float, nullable=True)
    new_value = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    is_sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_unsent_alerts', 'is_sent', 'created_at'),
    )

class WatchlistItem(Base):
    """قائمة المراقبة"""
    __tablename__ = 'watchlist'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(50), index=True, nullable=False)
    crypto_name = Column(String(255), nullable=False)
    symbol = Column(String(10), nullable=False)
    target_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_watchlist_crypto', 'crypto_id'),
    )

class AnalysisResult(Base):
    """نتائج التحليل"""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(50), index=True, nullable=False)
    crypto_name = Column(String(255), nullable=False)
    momentum_score = Column(Float, nullable=True)  # 0-100
    growth_score = Column(Float, nullable=True)  # 0-100
    risk_score = Column(Float, nullable=True)  # 0-100
    overall_score = Column(Float, nullable=True)  # 0-100
    recommendation = Column(String(50), nullable=True)  # HIGH, MEDIUM, LOW
    analysis_details = Column(Text, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_analysis_score', 'overall_score', 'analyzed_at'),
    )

class TwitterMention(Base):
    """أحاديث التويتر عن العملات"""
    __tablename__ = 'twitter_mentions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(50), index=True, nullable=True)
    crypto_name = Column(String(255), nullable=True)
    tweet_id = Column(String(100), unique=True, index=True)
    author = Column(String(255), nullable=False)
    tweet_text = Column(Text, nullable=False)
    likes = Column(Integer, nullable=True)
    retweets = Column(Integer, nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    mentioned_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_mentions_crypto', 'crypto_id', 'mentioned_at'),
    )

class User(Base):
    """المستخدمون"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    api_key = Column(String(100), unique=True, nullable=False, index=True)
    notification_email = Column(Boolean, default=True)
    notification_telegram = Column(Boolean, default=False)
    telegram_chat_id = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# إنشاء قاعدة البيانات
def init_db():
    """تهيئة قاعدة البيانات"""
    engine = create_engine(Config.DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """الحصول على جلسة قاعدة البيانات"""
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()
