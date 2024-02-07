from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from config.db import engine
from models.User import User
from passlib.context import CryptContext
from schema.users import UserPrivate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

def create_token(name):
    access_token = {"sub":name,
                    "exp":datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
                    }
    return {"access_token": jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM),"token_type":"JWT"}

def validate_user(anb,password):
    with engine.connect() as conection:
        try:
            user = conection.execute(User.select().where(User.c.anb == anb)).first()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user incorrected, please try again in a few seconds")
        
        if not (pwd_context.verify(password,user._asdict()['password'])):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password incorrected, please try again in a few seconds")
    return user._asdict()

def decode(tk:str):
    try:
        user = jwt.decode(tk,SECRET_KEY,ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=401,detail="Credenciales de auth invalidas", headers={"WWW-Authenticate":"Bearer"})
    return user

def search_decode(user):
    with engine.connect() as conection:
        try:
            result = conection.execute(User.select().where(User.c.name == user["sub"])).first()._asdict()
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found in the database")
    return result

def auth_user(tk:str = Depends(OAuth2PasswordBearer('/login'))):
    return UserPrivate(**search_decode(decode(tk)))
    