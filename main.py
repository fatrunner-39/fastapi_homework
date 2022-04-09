from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

import secrets
import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Создаем пользователя
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


def get_current_username(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, credentials.username)
    correct_username = secrets.compare_digest(credentials.username, user.username)
    correct_password = crud.verify_password(credentials.password, user.hashed_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Получаем текущего пользователя
@app.get("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


# Получаем всех пользователей
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# Получаем одного пользователя, используя id
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Создаем склад
@app.post("/warehouses/", response_model=schemas.Warehouse)
def create_warehouse(
    warehouse: schemas.WarehouseCreate, db: Session = Depends(get_db),
    username: str = Depends(get_current_username)
):
    user = crud.get_user_by_username(db, username)
    if not user.is_seller:
        raise HTTPException(status_code=403, detail="Only seller can add items!")
    return crud.create_warehouse(db=db, user_id=user.id, warehouse=warehouse)


# Получаем все склады
@app.get("/warehouses/", response_model=list[schemas.Warehouse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    warehouses = crud.get_warehouses(db, skip=skip, limit=limit)
    return warehouses


# Получаем одного пользователя, используя id
@app.get("/warehouses/{warehouse_id}", response_model=schemas.Warehouse)
def read_item(warehouse_id: int, db: Session = Depends(get_db)):
    item = crud.get_warehouse_by_id(db, warehouse_id)
    return item


'''Покупка товара. Входящие данные: id товара, количество товара, которое покупают.
Продавцы не могут покупать товар, если количество товара на складе равно 0,
то получаем ошибку 404, если покупатель просит больше товара, чем есть на складе, 
выбрасываем ошибку с подписью, что товара недостаточно в количестве...'''
@app.put("/warehouses/{warehouse_id}/buy/", response_model=schemas.Warehouse)
def buy_item(warehouse_id: int, warehouse: schemas.WarehouseUpdate, db: Session = Depends(get_db),
             username: str = Depends(get_current_username)):
    user = crud.get_user_by_username(db, username)
    prod = crud.get_warehouse_by_id(db, warehouse_id)
    balance = prod.quantity
    if user.is_seller:
        raise HTTPException(status_code=403, detail="Only customer can buy items!")
    if balance == 0:
        raise HTTPException(status_code=404, detail="No item!")
    if balance < warehouse.quantity:
        raise HTTPException(status_code=403, detail=f"Not enough {warehouse.quantity - balance} "
                                                     f"items!")

    balance -= warehouse.quantity
    item = crud.update_warehouse(db, warehouse_id, balance)
    return item

