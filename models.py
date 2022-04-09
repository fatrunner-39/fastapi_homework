from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    is_seller = Column(Boolean, default=True)   # If is_seller == False, it's customer

    items = relationship('Warehouse', back_populates='owner')


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, index=True)
    quantity = Column(Integer, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship(User, back_populates='items')
