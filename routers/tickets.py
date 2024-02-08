from fastapi import APIRouter,Depends
from utils.auth import auth_user
from models.Tickets import Tickets
from schema.users import UserPrivate
from schema.tickets import TicketsCreate,TicketsShow
from utils.users import get_user_by_anb,update_users_transaction
from utils.tickets import validate_tickets,create_ticket_db,get_tickets_by_receive_or_sent,create_ticket_obj,validate_tickets_add_money

router = APIRouter(prefix="/transaction")

@router.post('',status_code=201,response_model=TicketsShow)
async def create_transaction(ticket:TicketsCreate, user_send:UserPrivate = Depends(auth_user)):
        user_receive = get_user_by_anb(ticket.anb)
        ticket_validate = validate_tickets(user_send,user_receive, ticket)        
        update_users_transaction(user_send,user_receive,ticket_validate.amount)
        create_ticket_db(ticket_validate)
        return create_ticket_obj(user_send,user_receive,ticket.amount)

@router.get('/history/send',status_code=200,response_model=list[TicketsShow])
async def get_tickets_sent(user:UserPrivate = Depends(auth_user)):
   return get_tickets_by_receive_or_sent(user.id,Tickets.c.user_id_send)

@router.get('/history/received',status_code=200,response_model=list[TicketsShow])
async def get_tickets_receive(user:UserPrivate = Depends(auth_user)):
   return get_tickets_by_receive_or_sent(user.id,Tickets.c.user_id_receive)

@router.patch("/addmoney/{money:int}",status_code=200,response_model=TicketsShow)
async def add_money(money:int, user:UserPrivate = Depends(auth_user)):
      validate_tickets_add_money(money)
      ticket_validate = create_ticket_obj(user,user,money)
      update_users_transaction(user,user,money)
      create_ticket_db(ticket_validate)
      return ticket_validate      