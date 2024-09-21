
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




rules='''i have few templates which have characteristics as keywords.
        you have to give me a list of keywords that match the requirements of user input.
        include all the possible keywords which satisfy user requirements.
        include even remotely related keywords.
        following are the possible keywords:
        "12 months"
        "anomaly"
        "by business units"
        "by services"
        "Commitments"
        "committed services"
        "cost"
        "cost can be saved"
        "cost decrease"
        "cost increase"
        "cost saved"
        "cost Savings"
        "current month"
        "current month spending"
        "specific start and end month or date"
        "Decrease"
        "forecast spending"
        "for services"
        "increase"
        "increase in costs"
        "Jira"
        "last 12 months"
        "last 12 months cost"
        "last month cost"
        "last month spending"
        "last month usage"
        "month cost"
        "monthly"
        "oversees anomaly"
        "potential cost savings"
        "Radar"
        "radar cost decrease"
        "radar cost increase"
        "realized savings"
        "Real or actual cost saving"
        "Real or actual cost saving-month"
        "RI"'modifiedWidgets.json'
        "SP Fee"
        "spikes"
        "Spikes"
        "sudden"
        "sudden cost decrease"
        "sudden cost increase"
        "support fee"
        "tickets"
        "total"
        "Total cost for Specific month"
        "Total Usage"
        "Total usage for Specific month"
        "uncovered services"
        "usage"
        "usage charge"
        "yearly"
print(result)
    {{
    "keywords": ["keyword1", "keyword2", ...]
    }}
    if no keywords match return a empty keywords array.
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
    ids=set()
    try:

        # for debugging .. remove cb if wanted
        with get_openai_callback() as cb:
            response=gpt.invoke({'user_input':prompt})
        print('widget selection token-costs',cb.total_tokens,cb.prompt_tokens,cb.completion_tokens)
        keywords_list=response['keywords']
        for keyword in keywords_list:
            for obj in modwidgets:
                if keyword in obj['keywords']:
                    ids.add(obj['id'])
    except Exception as e:
        print('error',e)
    return list(ids)

if __name__=='__main__':
    userinput=input('Enter prompt')
    print(getWidgetIds(userinput))
