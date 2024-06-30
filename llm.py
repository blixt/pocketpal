import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


def openai_prompt(prompt: str) -> str:
    chat = ChatOpenAI(model_name="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))
    messages = [HumanMessage(content=prompt)]
    response = chat.invoke(messages)
    return response.content
