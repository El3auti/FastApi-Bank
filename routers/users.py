from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.auth import create_token,validate_user,auth_user
from utils.users import create_user
from sqlalchemy.exc import SQLAlchemyError
from schema.users  import LoginUser,UserCreate,UserPublic,UserPrivate
from models.User import User
from config.db import engine

router = APIRouter(
    prefix="/bank"
)

@router.post('/user/create',status_code=201)
async def create_user(user:UserCreate):
    with engine.connect() as conection:
        try:
            conection.execute(User.insert().values(create_user(user)))
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
            raise HTTPException(status_code=500, detail=str(e))

@router.get('/user/{anb:int}',status_code=200)
async def get_user(anb:int):
    with engine.connect() as conection:
        try:
            return UserPrivate(**conection.execute(User.select().where(User.c.anb == anb)).first()._asdict())
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user anb incorrected, please try again in a few seconds")

oauth = OAuth2PasswordBearer(tokenUrl="/login")
@router.post('/login')
async def login_user(user:LoginUser = Depends()):
    user_validated = validate_user(user.anb,user.password)
    return create_token(user_validated["name"])

@router.patch("user/addmoney/{money:int}",status_code=201)
async def add_money(money:int, user:UserPrivate = Depends(auth_user)):
    with engine.connect() as conection:
        conection.execute(User.update().where(User.c.id == user.id).values(money = money))
        conection.commit()
    return {"SUCCESS YOU ARE RICH"}






