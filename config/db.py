from sqlalchemy import create_engine,MetaData
    
engine = create_engine('mysql+pymysql://root:sqlserver@localhost:3306/fastapi_bank')

meta_data = MetaData()