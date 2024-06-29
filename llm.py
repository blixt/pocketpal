import os
from langchain_openai import OpenAI

def openai_prompt(prompt: str)->str:
    llm = OpenAI(model_name='gpt-3.5-turbo-instruct', openai_api_key=os.getenv("OPENAI_API_KEY"))
    return llm.invoke(prompt)
