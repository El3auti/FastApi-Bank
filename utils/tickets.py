from fastapi import HTTPException,status
from schema.users import UserPrivate
from schema.tickets import TicketsShow
from config.db import engine
from models.Tickets import Tickets
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

def validate_tickets(user_send:UserPrivate,user_recibe:UserPrivate,ticket):
        # Si el usuario que envía es el mismo que el que recibe, lanza un error
        if user_send.anb == user_recibe.anb:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found in the database")
        
        # Si el usuario que envía no tiene suficiente dinero, lanza un error
        if user_send.money < ticket.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")
        
        
        
def validate_tickets_add_money(money):
    if money <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")
    
    


def create_ticket_obj(user_send:UserPrivate,user_recibe:UserPrivate,amount):
    return TicketsShow(user_id_receive=user_recibe.id,user_id_send=user_send.id,
                           timestamp=datetime.now(),amount=amount)


def create_ticket_db(ticket):
    # Establece una conexión con la base de datos
    with engine.connect() as conection:
        try:
           # Intenta insertar el ticket en la base de datos
           conection.execute(Tickets.insert().values(dict(ticket)))
        except SQLAlchemyError as e:
            # Si algo sale mal, revierte la transacción y lanza un error
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        

def get_tickets_by_receive_or_sent(user_id:int,field):
      # Establece una conexión con la base de datos
      with engine.connect() as conection:
        # Devuelve una lista de objetos TicketsShow para todos los tickets que coinciden con el campo dado
        return [TicketsShow(**ticket._asdict()) for ticket in conection.execute(Tickets.select().where(field == user_id))]
