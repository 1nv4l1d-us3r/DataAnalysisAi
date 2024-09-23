
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




rules='''i have few templates which are to be displayed based on the user input.
        you have to give me a list of template ids that match the requirements of user input.
        you have to select the template based on how well the description meets the user input.
        include all the possible templates which satisfy user requirements.
        id - description
        1 - "provides total cost spent for a given month based on 'Usage Charges', 'SP Fee', 'RI Fee' and 'Support Fee' and compares it with previous month. Implements bar graph for visualization"
        2 - "Describes the cloud usage for the given month and compares it with the previous month."
        3 - "describes total cost spent for a given 12 months period on 'Usage Charges', 'SP Fee', 'RI Fee' and 'Support Fee'. This date or months can be from YYYYMM to YYYYMM . This can have range of months or dates. Implements bar graph for visualization"
        4 - "Gives only an overview. Radar is like an invigilator, oversees anomaly, spikes, and activities which may result in sudden increase or decrease in cost"
        5 - "Radar is like an invigilator, oversees anomaly, spikes, and activities which may result in sudden increase in cost. This widget is specific to cost increase."
        6 - "Radar is like an invigilator, oversees anomaly, spikes, and activities which may result in sudden decrease in cost. This widget is specific to cost decrease."
        7 - "Gives a brief overview for rightsizing opportunities which refers to identifying potential areas where the company can adjust its resources to save on cost. Gives information for how much cost can be saved, yearly and monthly based on services and business units. Fetches rightsizing data for various services and implements bar chart for visualization."
        8 - "Describes the potential savings due to rightsizing opportunities. Gives month wise as well as year wise insights based on services"
        9 - "Track the details of Jira tickets. Implements pie chart for visualization"
        10 - "Realized savings refer to the actual, measurable cost reductions that a company has successfully achieved. Fetches realized savings data for various services for a given month"
        11 - "Realized savings refer to the actual, measurable cost reductions that a company has successfully achieved.This date or months can be from YYYYMM to YYYYMM.This can have range of months or dates. Fetches realized savings data for various services for the last 12 months"
        12 - "Describes total cost spent for current month, has three attributes: 'spend till date', 'last month spending', 'forecast spending'. Implements line chart for visualization "
        13 - "Gives information about committed services under SP, RI and also uncovered services. Implements pie chart for visualization"

    output format:

    [templateid1,templateid2, ....]

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
    widgetlist=[]
    try:
        # for debugging .. remove cb if wanted
        with get_openai_callback() as cb:
            response=gpt.invoke({'user_input':prompt})
        print('widget selection token-costs',cb.total_tokens,cb.prompt_tokens,cb.completion_tokens)
        widgetlist=response
    except Exception as e:
        print('error',e)
    return list(widgetlist)

if __name__=='__main__':
    userinput=input('Enter prompt')
    print(getWidgetIds(userinput))
