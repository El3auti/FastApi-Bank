from pydantic import BaseModel 
from datetime import datetime



class TicketsCreate(BaseModel):
    amount:int
    anb:int

class TicketsShow(BaseModel):
    user_id_send:int
    user_id_receive:int
    timestamp:datetime
    amount:int     
