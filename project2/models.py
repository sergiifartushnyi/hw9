from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    ipn = Column(String(20), unique=True)
    full_name = Column(String(150), nullable=False)
    contacts = Column(String(150))
    photo = Column(String(150))

    items = relationship("Item", back_populates="owner")
    contracts_leaser = relationship("Contract", foreign_keys="Contract.leaser_id", back_populates="leaser")
    contracts_taker = relationship("Contract", foreign_keys="Contract.taker_id", back_populates="taker")
    search_history = relationship("SearchHistory", back_populates="user")
    favorites = relationship("Favorites", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="author")

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(150))
    name = Column(String(50), unique=True)
    description = Column(String(250))
    price_hour = Column(REAL)
    price_day = Column(REAL)
    price_week = Column(REAL)
    price_month = Column(REAL)
    owner_id = Column(Integer, ForeignKey('user.id'))

    owner = relationship("User", back_populates="items")
    contracts = relationship("Contract", back_populates="item")
    favorites = relationship("Favorites", back_populates="item")

class Contract(Base):
    __tablename__ = 'contract'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    contract_num = Column(String(50), unique=True)
    leaser_id = Column(Integer, ForeignKey('user.id'))
    taker_id = Column(Integer, ForeignKey('user.id'))
    item_id = Column(Integer, ForeignKey('item.id'))

    leaser = relationship("User", foreign_keys=[leaser_id], back_populates="contracts_leaser")
    taker = relationship("User", foreign_keys=[taker_id], back_populates="contracts_taker")
    item = relationship("Item", back_populates="contracts")

class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    search_text = Column(String(150))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="search_history")

class Favorites(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    item_id = Column(Integer, ForeignKey('item.id'))

    user = relationship("User", back_populates="favorites")
    item = relationship("Item", back_populates="favorites")

class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    text = Column(Text)
    grade = Column(Integer)
    contract_id = Column(Integer, ForeignKey('contract.id'))

    author = relationship("User", foreign_keys=[author_id], back_populates="feedbacks")


