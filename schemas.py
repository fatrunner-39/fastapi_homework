from typing import List
from pydantic import BaseModel


class WarehouseBase(BaseModel):
    quantity: int


class WarehouseCreate(WarehouseBase):
    item: str


class WarehouseUpdate(WarehouseBase):
    pass


class Warehouse(WarehouseBase):
    id: int
    item: str
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    username: str
    password: str
    is_seller: bool


class UserAuthenticate(UserBase):
    password: str


class User(UserBase):
    id: int
    username: str
    is_seller: bool
    items: List[Warehouse] = []

    class Config:
        orm_mode = True
