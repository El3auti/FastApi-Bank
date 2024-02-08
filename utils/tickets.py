from fastapi import HTTPException,status
from schema.users import UserPrivate
from schema.tickets import TicketsShow
from config.db import engine
from models.Tickets import Tickets
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

def validate_tickets(user_send:UserPrivate,user_recibe:UserPrivate,ticket):
        if user_send.anb == user_recibe.anb:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found in the database")
        
        if user_send.money < ticket.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")
        
        
        
def validate_tickets_add_money(money):
    if money <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")
    
    


def create_ticket_obj(user_send:UserPrivate,user_recibe:UserPrivate,amount):
    return TicketsShow(user_id_receive=user_recibe.id,user_id_send=user_send.id,
                           timestamp=datetime.now(),amount=amount)


def create_ticket_db(ticket):
    with engine.connect() as conection:
        try:
           conection.execute(Tickets.insert().values(dict(ticket)))
        except SQLAlchemyError as e:
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        

def get_tickets_by_receive_or_sent(user_id:int,field):
      with engine.connect() as conection:
        return [TicketsShow(**ticket._asdict()) for ticket in conection.execute(Tickets.select().where(field == user_id))]
