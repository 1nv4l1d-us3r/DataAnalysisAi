from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from essentials import create_new_thread,chat_with_assistant


app = FastAPI()


# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))


class Prompt(BaseModel):
    text: str

app.mount("/resources", StaticFiles(directory=script_dir+"/resources"), name="resources")

@app.get("/")
async def read_root():
    return FileResponse(script_dir+'/indexgpt.html')


@app.get("/newConversation")
async def new_conversation():
    print('creating new Thread')
    create_new_thread()
    return 'ok'



@app.post("/sendPrompt")
async def send_prompt(request: Request ):
    try:
        # Process the prompt here
        body = await request.json()
        
        # Access the 'prompt' key directly
        prompt = body.get("prompt")

        if prompt=='test':
            text={'type':'text','data':'Here is the information that you asked'}
            table={"type":"table","data":{"columns":["Name","Age","City","Occupation","Salary"],"rows":[["John Doe",28,"New York","Engineer",70000],["Jane Smith",34,"Los Angeles","Designer",85000],["Michael Brown",42,"Chicago","Manager",95000],["Emily Davis",29,"Houston","Developer",72000],["David Wilson",37,"Miami","Consultant",88000],["Sarah Johnson",31,"San Francisco","Architect",93000],["Chris Lee",45,"Seattle","Scientist",100000],["Jessica Taylor",26,"Boston","Data Analyst",68000],["James Martin",40,"Denver","Lawyer",110000],["Laura Garcia",33,"Phoenix","Doctor",120000]]}}
        
            return {'messages':[text,table]}
        
        try:
            response=chat_with_assistant(prompt)
        except Exception as e:
            raise(e)

        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)