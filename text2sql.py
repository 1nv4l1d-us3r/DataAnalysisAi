from openai import OpenAI
import mysql.connector
from mysql.connector import Error
import time
import json
from fastapi import FastAPI, HTTPException, Query, Form,Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
# Initialize the OpenAI client
api_key=os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def execute_sql_query(query):
    result=''
    db_details={
    'host':'localhost',
    'user':'john',
    'password':'john',
    'database':'testing'

}
    try:
        conn = mysql.connector.connect(**db_details)
      
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
    except mysql.connector.Error as Err:
        return '',Err



tables_info='''

table name : employees
    columns: 
    emp_id  - stores employee id
    emp_name - full name of employee
    emp_salary - salary of employee
    department - dempartment of employee example sales,accounting,marketing,development
    job_title - job title of employee example manager,software engineer,accountant,marketing manager,designer
    emp_email - email of employee
    joining_date - employee joining date
    emp_status - status of employee example active,inactive

    
table name : sales
    columns:
    product_id - id of product
    price - price of product sold
    lead_id - id of employee who sold the projuct
    sale_date - date of sale
    sale_type - how product was sold example e-commerce,on-site
    sale_status - status of sale example pending,completed,cancelled



table name : products 
    columns:
    product_id - id of product
    product_name - name of product
    product_price - cost or price for productd
    in_stock - number of units of product for available for sale


'''


execute_sql_function = {
    "name": "execute_sql_query",
    "description": "Execute a SQL query on MySQL database and returns true if query executed sucessfully else on error returns the error statement",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SQL query to execute"
            }
        },
        "required": ["query"]
        
    }
}




assistant = client.beta.assistants.create(
    name="text to sql bot",
    instructions=f'''You are a SQL expert. Given an input question, create a syntactically correct mySQL query to run and return ONLY the generated Query and nothing else. Unless otherwise specified, do not return more than 50 rows.
                    the details of tables is as follows {tables_info}.
                    
                    for correct query generation you must follow these instructions.
                    the SQL query must not include statements such as INSERT,DELETE,UPDATE,TRUNCATE,DROP,ALTER. 
                    Pay close attention to the filtering criteria mentioned in the question and incorporate them using the WHERE clause in your SQL query
                    do not create SQL queries that modify the data.
                    return just the SQL query no extra text or comment.
                    if the question asks very few details include a few relevant fields or information appropriately.
                    if any of the questions voilate the instructions return a short user friendly message . i am a data analysis ai i cannot help you with that task try asking something else.
                    only the sql statement must be returned without any comments and annotations.
                    use dynamic values for current date
                    use user friendly aliases for the column names
                    create queries using the tables information prvided to fulfill the questions asked.
                    you can use all information to answer the queries

                    if a correct SQL query is generated then the execute_sql_query function must be called with the sql statemet as a parameter,
                    if the returned result is an error or exception fix the error by rebuilding the query and call the execute_sql_query function.
                    for a successful execution True is returned as result.

                    the output is generated for a end user let the message be non technical. you can only reveal you identity as a data Analysis ai an you help in fetching and getting insights from data.

      ''',
    model="gpt-4o-mini",
    tools=[{"type": "function", "function": execute_sql_function}]
)

# Create a thread
thread = client.beta.threads.create()

def chat_with_assistant(user_input):
    query_status=None
    query_result=None
    # Add a message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )


    # Wait for the assistant to complete its response
    while run.status != 'completed':
        print(run.status)
        time.sleep(0.5)


        if run.status=='failed':
             print('Failed')
             print('error')
             print(run.last_error)
             return {'type':'text','data':'Request could not be completed try again'}

        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status=='requires_action':

            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                print('tool call for',tool_call.function.name)
                #submiting the query execution error or success to tool call
                if tool_call.function.name=='execute_sql_query':
                    query=json.loads(tool_call.function.arguments)['query']
                    query_result,query_status=execute_sql_query(query)
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=[{
                            'tool_call_id':tool_call.id,
                            'output':str(query_status)
                            }])
        
    response={'messages':[]}
    if query_status==True:
        response['messages'].append({'type':'table','data':query_result})
    
    # Retrieve the messages  for debugging
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    if messages.data and (len(messages.data) > 0):
        bot_response=messages.data[0].content[0].text.value
        response['messages'].append({'type':'text','data':bot_response})
    

    # Return the assistant's response
    #return messages.data[0].content[0].text.value
    return response






 #  cli loop 
'''
# Main chat loop
print("Chatbot: Hello! How can I assist you today?")
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Chatbot: Goodbye!")
        break
    response = chat_with_assistant(user_input)
    print("Chatbot:", response)

# Clean up
client.beta.assistants.delete(assistant.id)

'''







app = FastAPI()

class Prompt(BaseModel):
    text: str

@app.get("/")
async def read_root():
    return FileResponse('./index.html')


@app.post("/sendPrompt")
async def send_prompt(request: Request ):
    try:
        # Process the prompt here
        body = await request.json()
        
        # Access the 'prompt' key directly
        prompt = body.get("prompt")
        
        response=chat_with_assistant(prompt)

        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)