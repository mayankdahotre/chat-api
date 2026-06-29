# from fastapi import FastAPI
# from openai import OpenAI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os

# load_dotenv()

# app = FastAPI()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# class PromptRequest(BaseModel):
#     prompt: str

# @app.post("/chat")
# def ask(req: PromptRequest):
#     ans = client.responses.create(
#         model="gpt-4o-mini",
#         input=req.prompt
#     )
#     return {"answer": ans.output_text}




# from fastapi import FastAPI
# from openai import AzureOpenAI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os

# load_dotenv()

# app = FastAPI()

# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_version="2024-12-01-preview"  
# )

# class PromptRequest(BaseModel):
#     prompt: str

# @app.post("/chat")
# def ask(req: PromptRequest):
#     ans = client.responses.create(
#         model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
#         input=req.prompt
#     )
#     return {"answer": ans.output_text}





from fastapi import FastAPI
from openai import AzureOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", "MISSING_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://semantic-intelligence.openai.azure.com/"),
    api_version="2025-04-01-preview" 
)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/chat")
def ask(req: PromptRequest):
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    
    ans = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": req.prompt}]
    )
    return {"answer": ans.choices[0].message.content}