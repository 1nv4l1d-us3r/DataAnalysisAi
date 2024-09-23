
from openai import AssistantEventHandler
from openai.types.beta.threads import Message,Text
from typing_extensions import override
import json
from datetime import datetime

currentDate=str(datetime.now())

class EventHandler(AssistantEventHandler):



    def __init__(self,client):
        super().__init__()
        self.client=client
        self.messages = []
        self.tool_outputs = []

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

    @override
    def on_run_done(self):
        print('run successfully complete')

    

        
 
    @override
    def on_tool_call_done(self,tool_call):

        #for debugging 
        print('tool call done for ',tool_call.function.name)
        
        if tool_call.function.name=='display_widget':
            arguments=json.loads(tool_call.function.arguments)
            widget_id=arguments['widget_id']
            params=arguments['params']
            message=f"widget id {widget_id} \n arguments: {json.dumps(params)}"
            self.add_text_message(message)
            self.tool_outputs.append({"tool_call_id": tool_call.id, "output": "True"})
        
    def submit_tool_outputs(self ):
        print('submiting outputs to tool calls')
      # Use the submit_tool_outputs_stream helper
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=self.current_run.thread_id,
        run_id=self.current_run.id,
        tool_outputs=self.tool_outputs,
      ) as stream:
            stream.until_done()
        self.tool_outputs=[]
        print('done submiting')








display_widget_function1 = {
    "name": "display_widget",
    "description": "Displays a widget based on the widget_id and a dictionary of parameters for customization.",
    "parameters": {
        "type": "object",
        "properties": {
            "widget_id": {
                "type": "string",
                "description": "The ID of the widget to display"
            },
            "parameters": {
                "type": "object",
                "description": "A dictionary containing key-value pairs for widget customization",
                "additionalProperties": {
                    "type": "string",
                    "description": "Custom parameters for the widget"
                }
            }
        },
        "required": ["widget_id", "parameters"]
    }
}


display_widget_function = {
    "name": "display_widget",
    "description": "Displays a widget based on the widget_id and a list of customization parameters.",
    "parameters": {
        "type": "object",
        "properties": {
            "widget_id": {
                "type": "string",
                "description": "The unique identifier of the widget to display."
            },
            "params": {
                "type": "array",
                "description": "A list of customization parameters, where each item is an object containing a key-value pair.",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "The key representing the customization option (e.g., 'month', 'type')."
                        },
                        "value": {
                            "type": "string",
                            "description": "The value for the corresponding customization option."
                        }
                    },
                    "required": ["key", "value"]
                }
            }
        },
        "required": ["widget_id", "params"]
    }
}






def createChatAssistant(client):

    assistant = client.beta.assistants.create(
        name="Data Visualizaion Ai",
        instructions=f'''Your name is Fi, you are a Ai that will help users fetch details and gain insights about their cloud services their cost and usage.
                        based on the user input. you will display different insights using widgets.
                        in the starting of the conversation no widgest will be available.
                        if no widgets are available you must ask the user what insights he wants to see.
                        based on to user input determine the insights visualization widgets to be displayed.
                        the widgets have optional and required parameters. 
                        make sure that all the required parameter's values are filled based on the user inputs.
                        if any parameter has not been determines ask the user to enter value for the specific parameter 
                        do not bother the user to provide parameters values in formatted manner.
                        you can only ask the user to enter details in human friendly and natural language.
                        you are responsible for formating the parametrs in proper form.
                        you need to decide which widget needs to be added based on the descripton of widget and what information the user requires.
                        you must ask the user for details in a user friendly manner.
                        you must format the data according to requirements if not in proper format.
                        you can add widgets which i might have suggested before if they match the user requirements.

                        after asking all values for parameters you must call the display_widget tool call to dispay the paticular insights widget to user.
                        on a success full tool call True will be returned.
                        you can display up to 2 widgets for each user query.

                        do not reveal widget information to the user.
                        you help in understanding costs,usages and getting insights
                        todays date is {currentDate}


        ''',
        model="gpt-4o-mini",
        tools=[{"type": "function", "function": display_widget_function}]
    )
    return assistant