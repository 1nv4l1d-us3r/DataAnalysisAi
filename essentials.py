
from openai import OpenAI
from chatAssistant import EventHandler
import json
import time
from chatAssistant import createChatAssistant
from widgetsAi import getWidgetIds
import os

with open('widgets.json') as f:
    widgets=json.load(f)

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
    

def flat(twoDarray):
    result=set()
    for oneDarray in twoDarray:
        for item in oneDarray:
            result.add(item)
    return list(result)


widgetsIdsCache=[]

def chat_with_assistant(user_input):
    global widgetsIdsCache
    widgetIds=getWidgetIds(user_input)
    if not widgetIds==[]:
        if len(widgetsIdsCache)>4:
            widgetsIdsCache.pop(0)
        widgetsIdsCache.append(widgetIds)
    
    availableWidgets=flat(widgetsIdsCache)
    selectedWidgets=[]

    for w in widgets:
        if w['id'] in availableWidgets:
            trimmed_widget={ key:value for key,value in w.items() if key in ['id','descriptions','required_params','optional_params']}
            selectedWidgets.append(trimmed_widget)

    selectedWidgetsString=f'suggested widgets: {json.dumps(selectedWidgets)}'
    prompt=selectedWidgetsString+user_input
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # Run the assistant
    myEventHandler=EventHandler(client)

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