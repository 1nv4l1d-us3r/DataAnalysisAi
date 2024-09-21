
import snowflake.connector
import os 
import time
import re


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




def execute_sql_query(query):
    print('starting query execution')

    illegal_query = bool(re.search(r'\b(INSERT|UPDATE|DELETE|MERGE)\b', query, re.IGNORECASE))
    if illegal_query:
        return '','Query must contain only select statements'

    result=''

    try:
        conn=getConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        

        columns = [column[0] for column in cursor.description]
                    # Create a dictionary with 'columns' and 'data' keys
        formatted_results = {
                        'columns': columns,
                        'rows': rows
                    }
       # result=json.dumps(formatted_results, default=str)

        result=formatted_results

        return result,True
    except snowflake.connector.Error as Err:
        return 'error',Err
    finally:
        cursor.close()
        print('done querying')

