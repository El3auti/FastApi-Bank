from fastapi import APIRouter,Depends,HTTPException,status
from config.db import engine
from routers.users import auth_user
from models.User import User
from models.Tickets import Tickets
from schema.users import UserPrivate
from schema.tickets import TicketsCreate,TicketsShow
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

router = APIRouter(prefix="/bank")

@router.post('/transaction')
async def send_money(data:TicketsCreate, user:UserPrivate = Depends(auth_user)):
    with engine.connect() as conection:
        try:
            to_send = conection.execute(User.select().where(User.c.anb == data.anb)).first()._asdict()
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

        if user.id == to_send['id']:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found in the database")

        if user.money < data.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")
        
        ticket = {
            "user_id_send":user.id,
            "user_id_receive": to_send["id"],
            "timestamp": datetime.now(),
            "amount":data.amount
            }

        try:
            if user.money >= data.amount: 
                conection.execute(User.update().where(User.c.anb == data.anb).values(money = to_send["money"] + data.amount))
                conection.execute(User.update().where(User.c.anb == user.anb).values(money = user.money - data.amount))
                conection.execute(Tickets.insert().values(ticket))
                conection.commit()
        except SQLAlchemyError as e:
            conection.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
        return {"Transfer Details": TicketsShow(**ticket, time=ticket["timestamp"])}

@router.get('/transaction/historial/send')
async def get_tickets_sent(user:UserPrivate = Depends(auth_user)):
    with engine.connect() as conection:
        return [TicketsShow(**ticket._asdict(),time=ticket._asdict()["timestamp"]) for ticket in conection.execute(Tickets.select().where(Tickets.c.user_id_send == user.id))]


@router.get('/transaction/historial/recibe')
async def get_tickets_recibe(user:UserPrivate = Depends(auth_user)):
    with engine.connect() as conection:
        return [TicketsShow(**ticket._asdict(),time=ticket._asdict()["timestamp"]) for ticket in conection.execute(Tickets.select().where(Tickets.c.user_id_receive == user.id))]
