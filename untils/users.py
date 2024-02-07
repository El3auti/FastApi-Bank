from schema.users import UserCreate
from sqlalchemy.sql import select,func
from config.db import engine
from models.User import User


def generate_unique_account_number():
    with engine.connect() as connection:
        max_account_number = connection.scalar(select(func.max(User.c.anb)))
        if max_account_number is None:
            return 1000  
        return max_account_number + 1
        
def create_user(user:UserCreate):
    user_dict = dict(user)['anb'] = generate_unique_account_number()
    return user_dict

