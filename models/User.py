from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String,Boolean
from config.db import engine, meta_data

User = Table("users",meta_data,
             Column("id",Integer,primary_key=True),
             Column("anb",Integer,unique=True, nullable=False),
             Column("password", String(255),nullable=False),
             Column("name",String(50),nullable=False),
             Column("age",Integer,nullable=False),
             Column("isActive",Boolean, nullable=False, default= True),
             Column("money",Integer)
)

meta_data.create_all(engine)