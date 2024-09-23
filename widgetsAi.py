
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from  langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_community.callbacks import get_openai_callback

import json


modwidgetspath='modifiedWidgets.json'
modwidgets=None

# Load JSON file into a variable
try:
    with open(modwidgetspath, 'r') as file:
        modwidgets = json.load(file)
except:
    exit('Error opening file modified')
# Print the loaded data



model = ChatOpenAI(model="gpt-4o-mini")




rules='''
i have few templates which are used to show cloud services stats to the user.
they must be displayed based on the query asked by the user.
you must select all the tages that are relevent to user query
include all the possible tags which satisfy user query including remotely related tags.

following are the tags:
    commitments - related to  services the user is commited to  
    cost - related operation cost and spedings on services
    jira - shows info on projects and pending tickets
    radar - realated to  spikes, sudden surges and anomalies in usage to cloud servies
    righsizing - shows the opportunities of right sizing cloud servies
    savings - potential cost savings for user
    usage - show usage statistics of cloud services to user

output format:
    ["tag1","tag2",...]

if ther is no template that matches the user input return a empty array.
'''

input_template=''' 
User Input:
    {user_input}
    '''

prompt_template = ChatPromptTemplate.from_messages(
    [("system", rules), ("user", input_template)]
)

json_parser=SimpleJsonOutputParser()


gpt=prompt_template|model|json_parser


def getWidgetIds(prompt):
    selectedTags=[]
    widgetIds=set()
    try:
        # for debugging .. remove cb if wanted
        with get_openai_callback() as cb:
            selectedTags=gpt.invoke({'user_input':prompt})
        print('widget selection token-costs',cb.total_tokens,cb.prompt_tokens,cb.completion_tokens)
        for widget in modwidgets:
            if widget['tag'] in selectedTags:
                widgetIds.add(widget['id'])
    except Exception as e:
        print('error',e)
    return list(widgetIds)



def getWidgetTags(prompt):
    selectedTags=[]
    try:
        # for debugging .. remove cb if wanted
        with get_openai_callback() as cb:
            selectedTags=gpt.invoke({'user_input':prompt})
        print('widget selection token-costs',cb.total_tokens,cb.prompt_tokens,cb.completion_tokens)
        
    except Exception as e:
        print('error',e)
    return list(selectedTags)


if __name__=='__main__':
    userinput=input('Enter prompt\n')
    print(getWidgetTags(userinput))
