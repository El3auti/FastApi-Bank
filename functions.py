from sqlalchemy.sql import select,func
from config.db import engine
from models.User import User


def generate_unique_account_number():
    with engine.connect() as connection:
        stmt = select(func.max(User.c.anb))
        max_account_number = connection.scalar(stmt)
        if max_account_number is None:
            return 1000  
        else:
            return max_account_number + 1
    

