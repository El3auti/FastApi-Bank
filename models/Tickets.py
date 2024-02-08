from sqlalchemy import ForeignKey, Integer, Table,Column,DateTime
from config.db import meta_data,engine


Tickets = Table(
    "tickets", meta_data,
    Column("id", Integer, primary_key=True),
    Column("user_id_send", Integer, ForeignKey('users.id')),
    Column("user_id_receive", Integer, ForeignKey('users.id')),
    Column("timestamp", DateTime, nullable=False),
    Column("amount", Integer, nullable=False)
    )
meta_data.create_all(engine)