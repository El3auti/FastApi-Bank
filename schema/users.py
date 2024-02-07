from typing import Optional
from fastapi import HTTPException,status
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from config.db import engine
from models.User import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    name:str
    password:str
    age:int
    money:Optional[int]

    @validator('money')
    def money_must_be_positive(cls, value):
        if value < 0:
            raise ValueError("Invalid value: 'money' must be a positive number")
        return value

    @validator('age')
    def age_must_be_18_or_older(cls, value):
        if value < 18:
            raise ValueError("Invalid value: 'age' must be 18 or older.")
        return value
    
    @validator('password')
    def hash_password(cls, password):
        return pwd_context.hash(password)

class UserPrivate(BaseModel):
    id:int
    password:str
    name:str
    age:int
    isActive:bool
    money:int
    anb:int

class LoginUser(BaseModel):
    anb:int
    password:str



class UserPublic(BaseModel):
    anb:int
    name:str

