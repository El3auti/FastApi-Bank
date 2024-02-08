from schema.users import UserCreate, UserPrivate
from sqlalchemy.sql import select,func
from sqlalchemy.exc import SQLAlchemyError
from config.db import engine
from models.User import User
from fastapi import HTTPException, status


def generate_unique_account_number():
    with engine.connect() as connection:
        max_account_number = connection.scalar(select(func.max(User.c.anb)))
        if max_account_number is None:
            return 1000  
        return max_account_number + 1
        
def create_user(user:UserCreate):
    user_dict = dict(user)['anb'] = generate_unique_account_number()
    return user_dict

def get_user_by_anb(anb:int):
    with engine.connect() as conection:
        try:
            return UserPrivate(**conection.execute(User.select().where(User.c.anb == anb)).first()._asdict())
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user anb incorrected, please try again in a few seconds")


def update_users_transaction(user_send,user_receive,amount):
    with engine.connect() as conection:
        try:
            # Incrementa el dinero del user_receive
            conection.execute(User.update().where(User.c.anb == user_receive.anb).values(money = user_receive.money + amount))
            # Si user_send y user_receive son diferentes, disminuye el dinero del user_send
            if user_send.id != user_receive.id:
                conection.execute(User.update().where(User.c.anb == user_send.anb).values(money = user_send.money - amount))       
            conection.commit()
        except SQLAlchemyError as e:
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))