
import snowflake.connector
import os 
import time


username=os.environ.get('SNOWFLAKE_USERNAME')
password=os.environ.get('SNOWFLAKE_PASSWORD')
account=os.environ.get('SNOWFLAKE_ACCOUNT')
database=os.environ.get('SNOWFLAKE_DATABASE')
warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE')

db_details={
    'user':username,
    'password':password,
    'account':account,
    'database':database,
    'warehouse':warehouse,
    'schema':'DATA'
    }


connection=None

def getConnection():
    global connection

    if connection:
        if not connection.is_closed():
            return connection
        
    print('creating connection to snowflake')
    connstart=time.time()
    conn = snowflake.connector.connect(**db_details)
    connection=conn
    print('connection took',round(time.time()-connstart,2),'s')
    return conn
