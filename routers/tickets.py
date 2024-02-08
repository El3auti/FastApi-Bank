from fastapi import APIRouter,Depends
from utils.auth import auth_user
from models.Tickets import Tickets
from schema.users import UserPrivate
from schema.tickets import TicketsCreate
from utils.users import get_user_by_anb,update_users_transaction
from utils.tickets import validate_tickets,create_ticket_db,get_tickets_by_receive_or_sent,create_ticket_obj,validate_tickets_add_money

router = APIRouter(prefix="/bank")

@router.post('/transaction')
async def create_transaction(ticket:TicketsCreate, user_send:UserPrivate = Depends(auth_user)):
        # Recupera el usuario que recibirá el dinero basándose en el número de cuenta proporcionado en el ticket
        user_receive = get_user_by_anb(ticket.anb)
        
        # Valida los detalles de la transacción
        ticket_validate = validate_tickets(user_send,user_receive, ticket)
        
        # Actualiza los saldos de las cuentas de los usuarios que envían y reciben
        update_users_transaction(user_send,user_receive,ticket_validate.amount)
        
        # Crea un nuevo ticket en la base de datos
        create_ticket_db(ticket_validate)
        
        return create_ticket_obj(user_send,user_receive,ticket.amount)

@router.get('/transaction/history/send')
async def get_tickets_sent(user:UserPrivate = Depends(auth_user)):
   # Recupera los tickets recibidos por el usuario
   return get_tickets_by_receive_or_sent(user.id,Tickets.c.user_id_send)

@router.get('/transaction/history/received')
async def get_tickets_receive(user:UserPrivate = Depends(auth_user)):
   # Recupera los tickets recibidos por el usuario
   return get_tickets_by_receive_or_sent(user.id,Tickets.c.user_id_receive)

@router.patch("/transaction/addmoney/{money:int}",status_code=201)
async def add_money(money:int, user:UserPrivate = Depends(auth_user)):
      # Valida que la cantidad de dinero a añadir sea mayor que cero
      validate_tickets_add_money(money)

      # Crea un nuevo objeto de ticket para la transacción de añadir dinero
      ticket_validate = create_ticket_obj(user,user,money)

      # Actualiza el saldo del usuario en la base de datos para reflejar el dinero añadido
      update_users_transaction(user,user,money)

      # Guarda el nuevo ticket en la base de datos
      create_ticket_db(ticket_validate)

      return ticket_validate      