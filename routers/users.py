from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from functions import generate_unique_account_number
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from schema.User  import UserCreate,UserPublic,MoneyTransfer,UserPrivate
from models.User import User
from config.db import engine
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/Bank"
)

@router.post('/user/create',status_code=201)
async def create_user(user:UserCreate):
    with engine.connect() as conection:
        try:
            user_insert = dict(user)
            user_insert['anb'] = generate_unique_account_number()
            conection.execute(User.insert().values(user_insert))
            conection.commit()
        except SQLAlchemyError as e:
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    return user


@router.get('/users',status_code=200)
async def get_all_users():
    with engine.connect() as conection:
        try:
            return [UserPublic(**row._asdict()) for row in conection.execute(User.select()).fetchall()]
        except SQLAlchemyError as e:
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))

@router.get('/user/{anb:int}',status_code=200)
async def get_user(anb:int):
    with engine.connect() as conection:
        try:
            return UserPrivate(**conection.execute(User.select().where(User.c.anb == anb)).first()._asdict())
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user anb incorrected, please try again in a few seconds")

    

oauth = OAuth2PasswordBearer(tokenUrl="/login")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

@router.post('/login')
async def login_user(form:OAuth2PasswordRequestForm = Depends()):
    with engine.connect() as conection:
        try:
            user = conection.execute(User.select().where(User.c.name == form.username)).first()._asdict()
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user incorrected, please try again in a few seconds")
        
        try:
            if not (pwd_context.verify(form.password,user['password'])):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password incorrected, please try again in a few seconds")
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while checking the password.")

    access_token = {"sub":form.username,
                    "exp":datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
                    }
    
    return {"access_token": jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM),"token_type":"JWT"}


def auth_user(tk:str = Depends(OAuth2PasswordBearer('/login'))):
    try:
        user = jwt.decode(tk,SECRET_KEY,ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=401,detail="Credenciales de auth invalidas", headers={"WWW-Authenticate":"Bearer"})

    with engine.connect() as conection:
        try:
            result = conection.execute(User.select().where(User.c.name == user["sub"])).first()._asdict()
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found in the database")
    return UserPrivate(**result)


@router.patch('/transaction')
async def send_money(data:MoneyTransfer, user:UserPrivate = Depends(auth_user)):
    with engine.connect() as conection:
        try:
            to_send = conection.execute(User.select().where(User.c.anb == data.account_to_send)).first()._asdict()
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

        if user.id == to_send['id']:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found in the database")

        if user.money < data.money_to_send:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")

        try:
            if user.money >= data.money_to_send: 
                conection.execute(User.update().where(User.c.anb == data.account_to_send).values(money = to_send["money"] + data.money_to_send))
                conection.execute(User.update().where(User.c.anb == user.anb).values(money = user.money - data.money_to_send))
                conection.commit()
        except SQLAlchemyError as e:
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    return {"Transfer Details":{
        "send money":data.money_to_send, 
       "account from":data.account_to_send,
        "rest money":user.money - data.money_to_send
    }}

@router.patch("user/addmoney/{money:int}",status_code=201)
async def add_money(money:int, user:UserPrivate = Depends(auth_user)):
    with engine.connect() as conection:
        conection.execute(User.update().where(User.c.id == user.id).values(money = money))
        conection.commit()
    return {"SUCESS YOU ARE A RICH"}





