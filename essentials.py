
from openai import AssistantEventHandler,OpenAI
from openai.types.beta.threads import Message,Text
from typing_extensions import override
import json
import time
from dbConnection import execute_sql_query
from chatAssistant import createChatAssistant

import os



class EventHandler(AssistantEventHandler):


    def __init__(self):
        super().__init__()
        self.messages = []
        self.tool_outputs=[]
    

    def add_text_message(self,text):
        self.messages.append({'type':'text','data':text})
    
    def add_table(self,table):
        self.messages.append({'type':'table','data':table})

    
    @override
    def on_text_done(self, text:Text):
        self.add_text_message(text.value)
    
    @override
    def on_run_failed(self, error):
        self.add_text_message("could'nt complete your request run failed")

    def on_event(self,event):
        if event.event=='thread.run.requires_action':
           self.handle_tool_calls(event.data)
        if event.event=='thread.run.completed':
            run=event.data
            usage=run.usage
            print('assistant usage',usage.total_tokens,usage.prompt_tokens,usage.completion_tokens)


    @override
    def handle_tool_calls(self,data):

        
          

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            print('tool call initiated for ',tool.function.name)
            if tool.function.name=='execute_sql_query':
                query=json.loads(tool.function.arguments)['query']
                query_result,query_status=execute_sql_query(query)
                if query_status==True:
                    #suppose to add table into messages
                    print('trying to add table to message')
                    self.add_table(query_result)

                self.tool_outputs.append({"tool_call_id": tool.id, "output": str(query_status)})

        self.submit_tool_outputs(data.id)
        

    def submit_tool_outputs(self,run_id):
        print('submiting outputs to tool calls')
      # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=self.current_run.thread_id,
        run_id=run_id,
        tool_outputs=self.tool_outputs,
      ) as stream:
            stream.until_done()
        self.tool_outputs=[]
        print('done submiting')


api_key=os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
thread = client.beta.threads.create()
assistant=createChatAssistant(client)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

def get_thread():
    return thread

def create_new_thread():
    global thread
    client.beta.threads.delete(thread_id=thread.id)
    thread = client.beta.threads.create()    
    




def chat_with_assistant(user_input):

    # Add a message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Run the assistant
    myEventHandler=EventHandler()

    runstart=time.time()
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=myEventHandler,
        ) as stream:
        stream.until_done()
    print('run took',round(time.time()-runstart),'s')

    # Wait for the assistant to complete its 
    response={'messages':myEventHandler.messages}
   
    return response