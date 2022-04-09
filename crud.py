from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic
from passlib.context import CryptContext
import models
import schemas


security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=fake_hashed_password,
                          is_seller=user.is_seller)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_warehouses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Warehouse).offset(skip).limit(limit).all()


def get_warehouse_by_id(db: Session, warehouse_id: int):
    return db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()


def create_warehouse(db: Session, warehouse: schemas.WarehouseCreate, user_id: int):
    db_warehouse = models.Warehouse(**warehouse.dict(), user_id=user_id)
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def update_warehouse(db: Session, warehouse_id: int, quantity: int):
    item = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    item.quantity = quantity
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
